from dataclasses import dataclass, field

@dataclass
class IndicatorResponse: 
    have_written: bool = False
    policy_status: bool = False
    policy_premium: bool = False
    policy_date: bool = False
    face_amount: bool = False

