from django import forms
from django.contrib.auth.models import User


# import choices

class NewMemeForm(forms.Form):
    title = forms.CharField(max_length=40,
                            widget=forms.TextInput(attrs={'class': 'validate', 'placeholder': 'Title'}))
    top_caption = forms.CharField(max_length=40,
                                  widget=forms.TextInput(attrs={'class': 'validate caption-input',
                                                                'placeholder': 'Top Caption',
                                                                'id': 'top-caption-input'}))
    bottom_caption = forms.CharField(max_length=40,
                                     widget=forms.TextInput(attrs={'class': 'validate caption-input',
                                                                   'placeholder': 'Bottom Caption',
                                                                   'id': 'bottom-caption-input'}))
    background = forms.ImageField(label='Select a file', required=False,
                                  widget=forms.FileInput(attrs={'id': 'uploaded-image'}))
    thread_id = forms.CharField(max_length=20,
                                widget=forms.HiddenInput(), initial=None, required=False)
    reply_user_id = forms.CharField(max_length=20,
                                widget=forms.HiddenInput(), initial=None, required=False)
    tag = forms.CharField(max_length=20,
                          widget=forms.TextInput(attrs={'class': 'validate',
                                                        'placeholder': 'Tag',
                                                        'id': 'tag-input'}))
    TEXT_CLR_CHOICES = (('white', 'White'), ('blue', 'Blue'), ('red', 'Red'))
    # text_color = forms.CharField(max_length=20,
    #                              widget=forms.Select(choices=TEXT_CLR_CHOICES))
    text_color = forms.ChoiceField(choices=TEXT_CLR_CHOICES, widget=forms.Select(attrs={'class': 'browser-default'}))
    # TEXT_FNT_CHOICES = (('arial', 'Arial'),('times', 'Times New Roman'))
    # text_font = forms.ChoiceField(choices=TEXT_FNT_CHOICES, widget=forms.Select(attrs={'class': 'browser-default'}))


class SignUpForm(forms.Form):
    username = forms.CharField(max_length=20,
                               widget=forms.TextInput(attrs={'class': 'validate', 'placeholder': 'Username'}))
    first_name = forms.CharField(max_length=20,
                                 widget=forms.TextInput(attrs={'class': 'validate', 'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=20,
                                widget=forms.TextInput(attrs={'class': 'validate', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=100,
                             widget=forms.TextInput(attrs={'class': 'validate', 'placeholder': 'Email'}))
    password1 = forms.CharField(max_length=200,
                                widget=forms.PasswordInput(attrs={'class': 'validate', 'placeholder': 'Password'}))
    password2 = forms.CharField(max_length=200,
                                label='Confirm Password',
                                widget=forms.PasswordInput(
                                    attrs={'class': 'validate', 'placeholder': 'Confirm Password'}))

    def clean(self):
        cleaned_data = super(SignUpForm, self).clean()

        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords did not match.")

        return cleaned_data

    def clean_username(self):
        # Confirms that the username is not already present in the
        # User model database.
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__exact=username):
            raise forms.ValidationError("Username is already taken.")

        return username


class UpdateInfoForm(forms.Form):
    password1 = forms.CharField(max_length=200,
                                widget=forms.PasswordInput(attrs={'class': 'validate', 'id': 'password1'}),
                                required=False)
    password2 = forms.CharField(max_length=200,
                                widget=forms.PasswordInput(attrs={'class': 'validate', 'id': 'password2'}),
                                required=False)
    first_name = forms.CharField(max_length=40, required=False,
                                 widget=forms.TextInput(attrs={'class': 'validate', 'id': 'first_name'}))
    last_name = forms.CharField(max_length=40, required=False,
                                widget=forms.TextInput(attrs={'class': 'validate', 'id': 'last_name'}))
    email = forms.EmailField(max_length=40, required=False,
                             widget=forms.EmailInput(attrs={'class': 'validate', 'id': 'email'}))
    short_bio = forms.CharField(max_length=420, required=False,
                                widget=forms.Textarea(
                                    attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Introduce yourself!'}))
    image = forms.ImageField(required=False)
    current_password = forms.CharField(max_length=200,
                                       widget=forms.PasswordInput(attrs={'class': 'validate',
                                                                         'id': 'current_password'}))
    user_id = forms.CharField(max_length=30,
                              widget=forms.HiddenInput(), required=False, initial=None)

    def clean(self):
        cleaned_data = super(UpdateInfoForm, self).clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        short_bio = cleaned_data.get('short_bio')
        cur_password = cleaned_data.get('current_password')
        user_id = cleaned_data.get('user_id')
        user = User.objects.get(pk=user_id)
        if not user.check_password(cur_password):
            raise forms.ValidationError("Wrong Password!")
        if password1 and (not password1.strip()):
            raise forms.ValidationError("empty password")
        if password2 and (not password2.strip()):
            raise forms.ValidationError("empty confirm password")
        if (password1.strip() and (not password2.strip())) or \
                (password2.strip() and (not password1.strip())):
            raise forms.ValidationError("Please input password twice")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("password input don't match")

        if short_bio and (not short_bio.strip()):
            raise forms.ValidationError("Short_bio are spaces")

        return cleaned_data
