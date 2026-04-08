from pydantic import BaseModel, Field, field_validator


class NewTransactionSchema(BaseModel):
    amount: int = Field(gt=0, examples=[100])
    user_id: int = Field(gt=0, examples=[1])
    account_id: int = Field(gt=0, examples=[1])
    transaction_id: str = Field(examples=["5eae174f-7cd0-472c-bd36-35660f00132b"])
    signature: str | bytes = Field(examples=["7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"])

    class Config:
        validate_assignment = True

    @field_validator("signature")
    @classmethod
    def bytes_to_str(cls, value):
        if isinstance(value, bytes):
            return value.hex()
        return value

class TransactionSchema(NewTransactionSchema):
    id: int
