
import os

import pytest
from generator.object.genrule_obj import GenRuleObject


@pytest.fixture(scope="function")
def incomplete_rule():
    incomplete_rule = {}
    
    return incomplete_rule

@pytest.fixture(scope="function")
def complete_rule():
    complete_rule = {
        "crime": "Send Location via SMS",
        "permission": [
            "android.permission.SEND_SMS",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.ACCESS_FINE_LOCATION"
        ],
        "api": [
            {
                "class": "Landroid/telephony/TelephonyManager",
                "method": "getCellLocation",
                "descriptor": "()Landroid/telephony/CellLocation;"
            },
            {
                "class": "Landroid/telephony/SmsManager",
                "method": "sendTextMessage",
                "descriptor": "(Ljava/lang/String; Ljava/lang/String; Ljava/lang/String; Landroid/app/PendingIntent; Landroid/app/PendingIntent;)V"
            }
        ],
        "score": 4,
    }
    return complete_rule


class TestGenRuleObject:
    
    def test_init_with_incomplete_rule(self, incomplete_rule):
        with pytest.raises(KeyError):
            _ = GenRuleObject(incomplete_rule)

    def test_init_with_complete_rule(self, complete_rule):
        rule = GenRuleObject(complete_rule)

        assert all(rule.check_item) is False
        assert rule.crime == "Send Location via SMS"
        assert rule.permission == [
            "android.permission.SEND_SMS",
            "android.permission.ACCESS_COARSE_LOCATION",
            "android.permission.ACCESS_FINE_LOCATION",
        ]
        assert rule.api == [
            {
                "class": "Landroid/telephony/TelephonyManager",
                "method": "getCellLocation",
                "descriptor": "()Landroid/telephony/CellLocation;",
            },
            {
                "class": "Landroid/telephony/SmsManager",
                "method": "sendTextMessage",
                "descriptor": (
                    "(Ljava/lang/String; Ljava/lang/String;"
                    " Ljava/lang/String; Landroid/app/PendingIntent;"
                    " Landroid/app/PendingIntent;)V"
                ),
            },
        ]
        assert rule.score == 4