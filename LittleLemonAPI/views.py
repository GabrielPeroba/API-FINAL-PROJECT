from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.contrib.auth.models import User, Group
from django.shortcuts import get_object_or_404
from datetime import date 
from rest_framework.exceptions import ValidationError
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer
from .permissions import IsManager


class MenuItemsView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    

    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title'] 
    ordering_fields = ['price', 'category'] 
    
    def get_queryset(self):
        queryset = MenuItem.objects.all()
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category_id=category)
        return queryset
        
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return [IsManager()]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticatedOrReadOnly()]
        return [IsManager()]


class ManagersGroupView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        users = User.objects.filter(groups__name='Manager')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({'message': 'Usuário adicionado a Gerentes'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Forneça o username'}, status=status.HTTP_400_BAD_REQUEST)

class ManagersGroupRemoveView(APIView):
    permission_classes = [IsManager]

    def delete(self, request, userId):
        user = get_object_or_404(User, id=userId)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'message': 'Usuário removido de Gerentes'}, status=status.HTTP_200_OK)

class DeliveryCrewView(APIView):
    permission_classes = [IsManager]

    def get(self, request):
        users = User.objects.filter(groups__name='Delivery crew')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        username = request.data.get('username')
        if username:
            user = get_object_or_404(User, username=username)
            crew = Group.objects.get(name='Delivery crew')
            crew.user_set.add(user)
            return Response({'message': 'Usuário adicionado à equipe de entrega'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Erro: Forneça o username'}, status=status.HTTP_400_BAD_REQUEST)

class DeliveryCrewRemoveView(APIView):
    permission_classes = [IsManager]

    def delete(self, request, userId):
        user = get_object_or_404(User, id=userId)
        crew = Group.objects.get(name='Delivery crew')
        crew.user_set.remove(user)
        return Response({'message': 'Usuário removido da equipe de entrega'}, status=status.HTTP_200_OK)


class CartView(generics.ListCreateAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        menuitem = serializer.validated_data['menuitem']
        quantity = serializer.validated_data['quantity']
        unit_price = menuitem.price
        price = quantity * unit_price
        serializer.save(user=self.request.user, unit_price=unit_price, price=price)

    def delete(self, request):
        Cart.objects.filter(user=request.user).delete()
        return Response({'message': 'Carrinho esvaziado com sucesso'}, status=status.HTTP_200_OK)
    


class OrderView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all() 
        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user) 
        else:
            return Order.objects.filter(user=user) 

    def perform_create(self, serializer):
        
        cart_items = Cart.objects.filter(user=self.request.user)
        
        if not cart_items.exists():
            raise ValidationError('Seu carrinho está vazio!')
            
        total = sum([item.price for item in cart_items])
        
        order = serializer.save(user=self.request.user, total=total, date=date.today())
        
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price
            )
            
        cart_items.delete()

class SingleOrderView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='Manager').exists():
            return Order.objects.all()

        elif user.groups.filter(name='Delivery crew').exists():
            return Order.objects.filter(delivery_crew=user)

        else:
            return Order.objects.filter(user=user)

    def update(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists() or request.user.groups.filter(name='Delivery crew').exists():
            return super().update(request, *args, **kwargs)
        return Response({'message': 'Você não tem permissão para editar pedidos'}, status=status.HTTP_403_FORBIDDEN)

    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='Manager').exists():
            return super().destroy(request, *args, **kwargs)
        return Response({'message': 'Você não tem permissão para deletar pedidos'}, status=status.HTTP_403_FORBIDDEN)