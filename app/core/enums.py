import enum


class UserRole(str, enum.Enum):
    buyer = "buyer"
    seller_individual = "seller_individual"
    seller_store = "seller_store"
    admin = "admin"


class ItemCondition(str, enum.Enum):
    new = "new"
    like_new = "like_new"
    good = "good"
    fair = "fair"


class ItemStatus(str, enum.Enum):
    active = "active"
    reserved = "reserved"
    sold = "sold"
    deleted = "deleted"


class SellerType(str, enum.Enum):
    individual = "individual"
    store = "store"


class ContentType(str, enum.Enum):
    text = "text"
    image = "image"
    voice = "voice"


class ReportTargetType(str, enum.Enum):
    item = "item"
    user = "user"
    store = "store"


class ReportStatus(str, enum.Enum):
    pending = "pending"
    reviewed = "reviewed"
    resolved = "resolved"


class OrderStatus(str, enum.Enum):
    inquiry = "inquiry"
    reserved = "reserved"
    completed = "completed"
    cancelled = "cancelled"


class PaymentStatus(str, enum.Enum):
    initiated = "initiated"
    paid = "paid"
    failed = "failed"
    refunded = "refunded"
    voided = "voided"


KSA_CITIES = [
    "riyadh", "jeddah", "mecca", "medina", "dammam",
    "khobar", "dhahran", "taif", "tabuk", "abha",
    "khamis_mushait", "hail", "buraidah", "najran", "jizan",
    "yanbu", "al_qatif", "al_jubail", "al_ahsa", "sakaka",
]
