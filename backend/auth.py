# from datetime import datetime, timedelta
# from prisma import Prisma

# db = Prisma()

# async def store_otp(email: str, otp: str):
#     """ Store OTP in the database with a 5-minute expiry. """
#     expires_at = datetime.utcnow() + timedelta(minutes=5)

#     await db.otp.upsert(
#         where={"email": email.lower()},
#         update={"otp": otp, "expiresAt": expires_at},
#         create={"email": email.lower(), "otp": otp, "expiresAt": expires_at},
#     )

# async def verify_stored_otp(email: str, otp: str):
#     """ Verify OTP from the database. """
#     stored_otp_data = await db.otp.find_unique(where={"email": email.lower()})

#     if not stored_otp_data:
#         return False, "OTP not found. Please request a new one."

#     if datetime.utcnow() > stored_otp_data.expiresAt:
#         await db.otp.delete(where={"email": email.lower()})  # Delete expired OTP
#         return False, "OTP expired. Request a new one."

#     if otp != stored_otp_data.otp:
#         return False, "Invalid OTP"

#     await db.otp.delete(where={"email": email.lower()})  # Remove OTP after successful login
#     return True, "Login successful"
