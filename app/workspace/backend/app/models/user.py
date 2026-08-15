from pydantic import BaseModel, EmailAddress

class User(BaseModel):
    name: str
    email: EmailAddress
    age: int
```

This implementation defines a simple `User` model using the Pydantic library, which is a powerful tool for creating and validating data. The model includes fields for `name`, `email`, and `age`.