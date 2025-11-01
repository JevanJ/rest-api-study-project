from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import db
from sqlalchemy.exc import SQLAlchemyError
from models import TagModel, StoreModel, ItemModel
from schemas import TagSchema, TagAndItemSchema
from flask_jwt_extended import jwt_required

blp = Blueprint("Tags", "tags", description="Operations on tags")

@blp.route("/store/<int:store_id>/tag")
class TagInStore(MethodView):
    @jwt_required()
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)

        return store.tags.all()
    
    @jwt_required()
    @blp.arguments(TagSchema)
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        tag = TagModel(**tag_data, store_id=store_id)

        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return tag
    
@blp.route("/tag/<int:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        return tag
    
    @jwt_required()
    @blp.response(202, description="Deletes a tag if no item is linked to it.", example={"message": "Tag deleted."})
    @blp.alt_response(404, description="Tag not found.")
    @blp.alt_response(400, description="Tag is linked to one or more items. Tag cannot be deleted.")
    def delete(self, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        if not tag.items:
            db.session.delete(tag)
            db.session.commit()
            return {"message": "Tag deleted."}
        abort(400, message="Could not delete tag. Make sure tag is not linked to any items first.")

@blp.route("/tag/<int:item_id>/tag/<int:tag_id>")
class LinkTagToItem(MethodView):
    @jwt_required()
    @blp.response(200, TagAndItemSchema)
    def post(self, item_id, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        item = ItemModel.query.get_or_404(item_id)
        if tag.store_id != item.store_id:
            abort(400, message="Make sure tag and item belong to the same store before linking.")    
        item.tags.append(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {"message": "Tag linked to item", "item": item, "tag": tag}
    
    @jwt_required()
    @blp.response(200, TagAndItemSchema)
    def delete(self, item_id, tag_id):
        tag = TagModel.query.get_or_404(tag_id)
        item = ItemModel.query.get_or_404(item_id)

        item.tags.remove(tag)
        try:
            db.session.add(item)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {"message": "Tag unlinked from item", "item": item, "tag": tag}