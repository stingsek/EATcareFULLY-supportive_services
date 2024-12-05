# from sentence_transformers import SentenceTransformer, util
# from services.recommendation.factors.categories.categories_comparator import CategoriesComparator

# class SentenceTransformerComparator(CategoriesComparator):
#     def __init__(self, model: SentenceTransformer = SentenceTransformer('all-MiniLM-L6-v2')) -> None:
#         self.model = model

#     def compare(self, product_categories: str, user_categories: str) -> float:
#         product_categories_embedding = self.model.encode(product_categories, convert_to_tensor=True)
#         user_categories_embedding = self.model.encode(user_categories, convert_to_tensor=True)

#         similarity = util.pytorch_cos_sim(product_categories_embedding, user_categories_embedding)

#         return similarity.item()