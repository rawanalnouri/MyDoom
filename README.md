# WalletWizard
A Django Web application that allows users to track their expenditures.

# Team MyDoom Major Group project

## Team members
The members of the team are:
- Sabeeka Ahmed
- Lina Namoun
- Katia Bennamane
- Areeba Safdar
- Zahra Amaan
- Rawan Alnouri
- Abdulaziz Albanawi
- Imaan Ghafur
- Mohammad (Ruhan) Salam

## Project structure
The project is called `WalletWizard` (Spending Tracker Web Application).  It currently consists of a single app `walletwizard` where all functionality resides.

## Deployed version of the application
The deployed version of the application can be found at *[http://walletwizard.pythonanywhere.com/](http://walletwizard.pythonanywhere.com/)*

## Installation instructions
To install the software and use it in your local development environment, you must first set up and activate a local development environment.  From the root of the project:

```
$ virtualenv venv
$ source venv/bin/activate
```

Install all required packages:

```
$ pip3 install -r requirements.txt
```

Migrate the database:

```
$ python3 manage.py makemigrations
$ python3 manage.py migrate
```

Seed the development database with:

```
$ python3 manage.py seed
```

Run all tests with:
```
$ python3 manage.py test
```

## Sources
The packages used by this application are specified in `requirements.txt`

## Links used throughout the project
Notifications:
https://stackoverflow.com/questions/68241427/how-to-make-a-scrollable-dropdown-menu-in-bootstrap-5
https://medium.com/star-gazers/how-to-add-notifications-to-django-app-74df1dac984e
https://github.com/gauthamdasu/Mini-project-blog-codes/tree/master/Simple_Chat_App
https://www.youtube.com/watch?v=C8pYT1R8yo4&list=PLpyspNLjzwBkV1Lo2CSKLFtzG3PUNTG8q&index=10&ab_channel=CodeWithStein
https://www.w3schools.com/howto/howto_css_notification_button.asp

Automatic logout:
https://pypi.org/project/django-auto-logout/

User profile:
https://mdbootstrap.com/docs/standard/extended/profiles/

Images:
https://www.canva.com/en_gb/

Testimonial:
https://freefrontend.com/bootstrap-testimonials/

Side menu styling:
https://www.codingsnow.com/2021/01/sidebar-menu-with-sub-menu-dashboard.html

Users list pagination:
https://getbootstrap.com/docs/4.0/components/pagination/
https://nemecek.be/blog/105/how-to-use-elided-pagination-in-django-and-solve-too-many-pages-problem

User search bar:
Django Search Tutorial | LearnDjango.com

User, Testing and User follow functionality:
Clucker Django Project Final - Kings College London Year 2 Semester 1
