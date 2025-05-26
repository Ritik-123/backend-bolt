from django.contrib import admin
from users.models import User, PasswordResetOTP, SensorData


admin.site.register(User)
admin.site.register(PasswordResetOTP)
admin.site.register(SensorData)