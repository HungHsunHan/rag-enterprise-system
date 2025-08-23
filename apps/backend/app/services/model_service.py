from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db.models import LLMModel
from app.schemas.model import LLMModelCreate, LLMModelUpdate


def create_model(db: Session, model_data: LLMModelCreate) -> LLMModel:
    """
    Create a new LLM model
    """
    try:
        # If this is set as default, unset all other defaults
        if model_data.is_default:
            db.query(LLMModel).update({LLMModel.is_default: False})
        
        db_model = LLMModel(
            model_name=model_data.model_name,
            display_name=model_data.display_name,
            is_active=model_data.is_active,
            is_default=model_data.is_default
        )
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model
    except IntegrityError:
        db.rollback()
        raise ValueError("Model name already exists")


def get_models(db: Session, active_only: bool = False) -> List[LLMModel]:
    """
    Get all models, optionally filter by active status
    """
    query = db.query(LLMModel)
    if active_only:
        query = query.filter(LLMModel.is_active == True)
    
    return query.order_by(LLMModel.is_default.desc(), LLMModel.created_at.asc()).all()


def get_model_by_id(db: Session, model_id: str) -> Optional[LLMModel]:
    """
    Get model by ID
    """
    return db.query(LLMModel).filter(LLMModel.id == model_id).first()


def get_model_by_name(db: Session, model_name: str) -> Optional[LLMModel]:
    """
    Get model by name
    """
    return db.query(LLMModel).filter(LLMModel.model_name == model_name).first()


def get_default_model(db: Session) -> Optional[LLMModel]:
    """
    Get the default model
    """
    return db.query(LLMModel).filter(
        LLMModel.is_default == True, 
        LLMModel.is_active == True
    ).first()


def update_model(db: Session, model_id: str, model_data: LLMModelUpdate) -> Optional[LLMModel]:
    """
    Update model information
    """
    db_model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    if not db_model:
        return None
    
    # If setting as default, unset all other defaults first
    if model_data.is_default is True:
        db.query(LLMModel).update({LLMModel.is_default: False})
    
    for key, value in model_data.dict(exclude_unset=True).items():
        if value is not None:
            setattr(db_model, key, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model


def delete_model(db: Session, model_id: str) -> bool:
    """
    Delete model by ID
    """
    db_model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    if not db_model:
        return False
    
    # Don't allow deleting the default model
    if db_model.is_default:
        raise ValueError("Cannot delete the default model")
    
    db.delete(db_model)
    db.commit()
    return True


def set_default_model(db: Session, model_id: str) -> Optional[LLMModel]:
    """
    Set a model as the default
    """
    # Unset all defaults first
    db.query(LLMModel).update({LLMModel.is_default: False})
    
    # Set the specified model as default
    db_model = db.query(LLMModel).filter(LLMModel.id == model_id).first()
    if not db_model:
        return None
    
    db_model.is_default = True
    db_model.is_active = True  # Ensure default model is active
    
    db.commit()
    db.refresh(db_model)
    return db_model