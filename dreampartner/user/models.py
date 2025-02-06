from django.db import models

COMPATIBILITY = {
    "Aries": ["Leo", "Sagittarius"],
    "Taurus": ["Virgo", "Capricorn"],
    "Gemini": ["Libra", "Aquarius"],
    "Cancer": ["Scorpio", "Pisces"],
    "Leo": ["Aries", "Sagittarius"],
    "Virgo": ["Taurus", "Capricorn"],
    "Libra": ["Gemini", "Aquarius"],
    "Scorpio": ["Cancer", "Pisces"],    
    "Sagittarius": ["Aries", "Leo"],
    "Capricorn": ["Taurus", "Virgo"],
    "Aquarius": ["Gemini", "Libra"],
    "Pisces": ["Cancer", "Scorpio"],
}

GENDER_CHOICES = [
    ('Male', 'Male'),
    ('Female', 'Female'),
    ('Other', 'Other'),
]

ZODIAC_CHOICES = [(sign, sign) for sign in COMPATIBILITY.keys()]

class UserProfile(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birthdate = models.DateField(null=True, blank=True) 
    gender = models.CharField(max_length=6, choices=GENDER_CHOICES, null=True, blank=True)
    zodiac = models.CharField(max_length=20, choices=ZODIAC_CHOICES)
    picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    selected_match = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name="selected_by"
    )
    match_accepted = models.BooleanField(default=False)
    matches = models.ManyToManyField('self', symmetrical=False, related_name='matched_with', blank=True)

    def get_compatible_zodiacs(self):
        return COMPATIBILITY.get(self.zodiac, [])

    def get_all_matches(self):
        """Return all accepted matches."""
        return self.matches.all()

    def get_pending_requests(self):
        """Return all users who selected this user but haven't been accepted yet."""
        return self.selected_by.filter(match_accepted=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.zodiac}"

class Notification(models.Model):
    receiver = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="notifications")
    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="sent_notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.receiver.first_name} from {self.sender.first_name}"
