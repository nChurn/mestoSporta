from django.db import models

# Create your models here.


class Category(models.Model):
    is_active = models.BooleanField(default=True)
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        db_table = 'categories'

    def __str__(self):
    	return self.name

class City(models.Model):
	name = models.CharField(max_length=100, unique=True)
	is_active = models.BooleanField(default=True)
	
	class Meta:
		db_table = 'cities'

	def __str__(self):
		return self.name        

class User(models.Model):
    id = None
    telegram_id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    lang_code = models.CharField(max_length=4, default='ru_RU')
    role = models.CharField(max_length=100, default='user')

    is_subscribe = models.BooleanField(default=False)
    expires_in = models.DateTimeField(null=True, blank=True)


    class Meta:
        db_table='users'

    def __str__(self):
    	return self.first_name + f"<self.telegram_id>"

class Traning(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'tranings'

    def __str__(self):
    	return self.name

class Metro(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)

    class Meta:
        db_table = 'metros'

    def __str__(self):
    	return self.city + " " + self.name

class District(models.Model):
    name = models.CharField(max_length=100)
    city = models.CharField(max_length=100)


    class Meta:
        db_table = 'district'

    def __str__(self):
    	return self.city + " " + self.name

class Section(models.Model):
    title = models.CharField(max_length=100)
    address = models.CharField(max_length=128)

    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True)
    geoposition = models.CharField(max_length=32, unique=True)

    metro = models.ForeignKey(Metro, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    stars = models.IntegerField(default=0)
    rated_users_count = models.IntegerField(default=0)

    city = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    tranings = models.CharField(max_length=1000)

    is_active = models.BooleanField(default=False)

    class Meta:
        db_table = 'sections'

    def __str__(self):
    	if self.is_active:
    		return self.title + " (active)"
    	return self.title + " (not active)"


class SectionPhoto(models.Model):
	file_path = models.CharField(max_length=512)
	section = models.ForeignKey(Section, on_delete=models.CASCADE)

	def __str__(self):
		return self.section.title