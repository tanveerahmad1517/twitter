from django import forms

from .models import ImageBroadcast
from cloudinary.forms import CloudinaryJsFileField, CloudinaryUnsignedJsFileField 
from cloudinary.compat import to_bytes 
import cloudinary, hashlib 
class PostForm(forms.Form):
	image = CloudinaryJsFileField(required=False)