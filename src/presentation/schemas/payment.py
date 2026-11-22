from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.application.dtos.payment import PaymentOutput, ProcessPaymentInput

_SIGNATURE_EXAMPLE = "7b47e41efe564a062029da3367bde8844bea0fb049f894687cee5d57f2858bc8"


class ProcessPaymentRequest(BaseModel):
    model_config = ConfigDict(validate_assignment=True)

    amount: int = Field(gt=0, examples=[100])
    user_id: int = Field(gt=0, examples=[1])
    account_id: int = Field(gt=0, examples=[1])
    transaction_id: str = Field(examples=["5eae174f-7cd0-472c-bd36-35660f00132b"])
    signature: str = Field(examples=[_SIGNATURE_EXAMPLE])

    @field_validator("signature", mode="before")
    @classmethod
    def bytes_to_str(cls, value: object) -> object:
        if isinstance(value, bytes):
            return value.hex()
        return value

    def to_input(self) -> ProcessPaymentInput:
        return ProcessPaymentInput(
            transaction_id=self.transaction_id,
            account_id=self.account_id,
            user_id=self.user_id,
            amount=self.amount,
            signature=self.signature,
        )


class PaymentResponse(BaseModel):
    id: int
    amount: int
    user_id: int
    account_id: int
    transaction_id: str
    signature: str

    @classmethod
    def from_output(cls, output: PaymentOutput) -> "PaymentResponse":
        return cls(
            id=output.id,
            amount=output.amount,
            user_id=output.user_id,
            account_id=output.account_id,
            transaction_id=output.transaction_id,
            signature=output.signature,
        )
