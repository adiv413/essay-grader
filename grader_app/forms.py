from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from ckeditor.fields import RichTextField
from ckeditor.widgets import CKEditorWidget

from .models import User, Assignment


class CommentForm(forms.Form):
    Comment = forms.CharField(widget=forms.TextInput(
        attrs={
            "class": "form-control",
            "placeholder": "Leave a comment!"
        })
    )


dropdown = (("APA", "APA"), ("MLA", "MLA"))


class AssignmentForm(forms.Form):
    assignment_name = forms.CharField(max_length=150, widget=forms.TextInput(attrs={
        "class": "form-control",
        "placeholder": "Ex: Romeo and Juliet"
    })
                                      )
    assignment_description = forms.CharField(widget=forms.Textarea(
        attrs={
            "class": "form-control",
            "placeholder": "Ex: Write a 5 paragraph essay on why Romeo and Juliet is the best story ever"
        })
    )


class EssayForm(forms.Form):
    teachers = forms.ChoiceField(required=True, widget=forms.Select(attrs={'class': "form-control"}))
    assignment = forms.ModelChoiceField(queryset=Assignment.objects.all(), required=True, widget=forms.Select(attrs={'class': "form-control"}))
    title = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Title"
        })
    )
    body = forms.CharField(widget=CKEditorWidget)
    citation_type = forms.ChoiceField(choices=dropdown, required=True, widget=forms.RadioSelect)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(EssayForm, self).__init__(*args, **kwargs)
        if user is not None:
            temp = user.get_teachers()
            teachers = list(temp.keys())
            thingy = []
            for teacher in teachers:
                if temp[teacher] != "":
                    thingy.append((temp[teacher], temp[teacher]))

            if len(thingy) >= 1:
                thingy.insert(0, ("-SELECT-", "-SELECT-"))

            empty = False
            if len(thingy) == 0:
                empty = True
                thingy.append(("Please Add Your Teachers in Settings", "Please Add Your Teachers in Settings"))
                for field in list(self.fields.keys()):
                    self.fields.get(field).disabled = True
            print("thingy:-", thingy)
            self.fields['teachers'] = forms.ChoiceField(choices=thingy, required=True, disabled=empty, widget=forms.Select(attrs={'class': "form-control"}))


class LoginForm(forms.Form):
    email = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), max_length=150,
                               required=True)


class SetupForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"class": "form-control"}))
    FRESHMAN = 'FR'
    SOPHOMORE = 'SO'
    JUNIOR = 'JR'
    SENIOR = 'SR'
    GRADUATE = 'GR'
    YEAR_IN_SCHOOL_CHOICES = [
        (FRESHMAN, 'Freshman'),
        (SOPHOMORE, 'Sophomore'),
        (JUNIOR, 'Junior'),
        (SENIOR, 'Senior'),
        (GRADUATE, 'Graduate'),
    ]
    year_in_school = forms.ChoiceField(
        choices=YEAR_IN_SCHOOL_CHOICES,
        widget=forms.Select(attrs={'class': "form-control"})
    )


class ChangeForm(forms.Form):
    password_1 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), max_length=150,
                                 required=True)
    password_2 = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}), max_length=150,
                                 required=True)

    def disable(self):
        self.fields['password_1'].disabled = True
        self.fields['password_2'].disabled = True


class InfoForm(forms.Form):
    email = forms.EmailField(max_length=250,
                             widget=forms.TextInput(attrs={'readonly': 'readonly', "class": "form-control"}))
    first_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    middle_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))
    last_name = forms.CharField(max_length=50, widget=forms.TextInput(attrs={"class": "form-control"}))

    def disable(self):
        self.fields['first_name'].disabled = True
        self.fields['middle_name'].disabled = True
        self.fields['last_name'].disabled = True


class TeacherForm(forms.Form):
    period_1_teacher = forms.EmailField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Teacher Email"}), required=False)
    period_2_teacher = forms.EmailField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Teacher Email"}), required=False)
    period_3_teacher = forms.EmailField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Teacher Email"}), required=False)
    period_4_teacher = forms.EmailField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Teacher Email"}), required=False)
    period_5_teacher = forms.EmailField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Teacher Email"}), required=False)
    period_6_teacher = forms.EmailField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Teacher Email"}), required=False)
    period_7_teacher = forms.EmailField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control", "placeholder": "Teacher Email"}), required=False)


class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control"}))
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput(attrs={"class": "form-control"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"class": "form-control"}))

    class Meta:
        model = User
        fields = ('email',)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email=email)
        if qs.exists():
            raise forms.ValidationError("email is taken")
        return email

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2


class UserAdminCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = User
        fields = ('email', 'password', 'admin')

    def clean_password(self):
        return self.initial["password"]
