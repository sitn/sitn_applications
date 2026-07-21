from django.urls import path

from . import views

urlpatterns = [
    path("catalog.json", views.catalog_view, name="panoview-catalog"),
    path("collections", views.collections_view, name="panoview-collections"),
    path("collections/<str:seq_id>/collection.json", views.collection_view, name="panoview-collection"),
    path("collections/<str:seq_id>/items/<str:item_id>", views.item_view, name="panoview-item"),
    path("search", views.search_view, name="panoview-search"),
    # Catch-all: must stay last, matches the picture id in "/panoview/<item_id>?pic=...".
    path("<str:item_id>", views.panorama_view, name="panoview-panorama"),
]
