from fastapi import status
from app.exceptions.base import AppException


class CategoryNotFoundException(AppException):
    """Levée quand une catégorie est introuvable par son ID."""
    def __init__(self, category_id: int):
        super().__init__(
            message=f"La catégorie avec l'ID {category_id} n'a pas été trouvée.",
            status_code=status.HTTP_404_NOT_FOUND
        )


class CategoryAlreadyExistsException(AppException):
    """Levée quand le nom de catégorie est déjà utilisé."""
    def __init__(self, name: str):
        super().__init__(
            message=f"Une catégorie avec le nom '{name}' existe déjà.",
            status_code=status.HTTP_409_CONFLICT
        )


class CategoryHasProductsException(AppException):
    """Levée quand on tente de supprimer une catégorie qui possède encore des produits."""
    def __init__(self, category_id: int):
        super().__init__(
            message=(
                f"Impossible de supprimer la catégorie {category_id} : "
                "elle contient encore des produits."
            ),
            status_code=status.HTTP_409_CONFLICT
        )


class ProductNotFoundException(AppException):
    """Levée quand un produit est introuvable par son ID."""
    def __init__(self, product_id: int):
        super().__init__(
            message=f"Le produit avec l'ID {product_id} n'a pas été trouvé.",
            status_code=status.HTTP_404_NOT_FOUND
        )
