from django.urls import path, re_path
from cultural_places.swagger import schema_view
from cultural_places import views

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', views.CulturalPlacesView.as_view(), name='cultural_places'),
    path('places/<int:id>', views.CulturalPlaceView.as_view(), name='cultural_place'),
    path('places/', views.CreateCulturalPlaceView.as_view(), name='create_cultural_place'),
    path('places/<int:id>', views.EditCulturalPlaceView.as_view(), name='edit_cultural_place'),
]
