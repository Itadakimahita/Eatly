from rest_framework import serializers
from apps.services.models import Comment, Post, UserLike, UserSubscription
from apps.user.models import CustomUser
from apps.restaurant.models import Restaurant

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'name', 'email']

class RestaurantShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['id', 'name']

class PostListSerializer(serializers.ModelSerializer):
    restaurant = RestaurantShortSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    comments_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'restaurant',
            'title',
            'description',
            'image_url',
            'created_at',
            'likes_count',
            'comments_count',
        )

class PostLikeSerializer(serializers.ModelSerializer):
    restaurant = RestaurantShortSerializer(read_only=True)
    likes_count= serializers.IntegerField(read_only=True)
    comments_count= serializers.IntegerField(read_only=True)

    class Meta:
        model=Post
        fields =(
            'id',
            'restaurant',
            'title',
            'description',
            'image_url',
            'created_at',
            'likes_count',
            'comments_count',
        )

class PostDetailSerializer(serializers.ModelSerializer):
    restaurant = RestaurantShortSerializer(read_only=True)
    likes_count= serializers.IntegerField(read_only=True)
    comments= serializers.SerializerMethodField(read_only=True)

    class Meta:
        model=Post
        fields =(
            'id',
            'restaurant',
            'title',
            'description',
            'image_url',
            'created_at',
            'likes_count',
            'comments',
        )

    def get_comments (self, obj):
        qs = obj.comments.order_by("created_at")[:50]
        return CommentSerializer(qs, many=True).data
    
class PostCreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model=Post
        fields =(
            'restaurant',
            'title',
            'description',
            'image_url',
        )
    def validate_restaurant(self, value):
        user = self.context['request'].user
        if value.owner != user:
            raise serializers.ValidationError("You can only create posts for your own restaurant.")
        return value
    
class CommentSerializer(serializers.ModelSerializer):
    user=UserShortSerializer(read_only=True)

    class Meta:
        model= Comment
        fields =(
            'id',
            'user',
            'content',
            'created_at',
            'post',
        )
        read_only_fields = ("id", "user", "created_at", "updated_at")   
    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)
    
class UserLikeSerializer(serializers.ModelSerializer):
    user=UserShortSerializer(read_only=True)
    discount_post=serializers.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model= UserLike
        fields =(
            'id',
            'user',
            'discount_post',
            'liked_at',
        )
        read_only_fields = ("id", "user", "liked_at")   
    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)

class UserSubscriptionSerializer(serializers.ModelSerializer):
    user=UserShortSerializer(read_only=True)
    restaurant=serializers.PrimaryKeyRelatedField(queryset=Restaurant.objects.all())

    class Meta:
        model= UserSubscription
        fields =(
            'id',
            'user',
            'restaurant',
            'subscribed_at',
        )
        read_only_fields = ("id", "user", "subscribed_at")   
    def create(self, validated_data):
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            validated_data["user"] = request.user
        return super().create(validated_data)