#needs cache abtraction
from flask_wtf import FlaskForm
from wtforms import IntegerField
from wtforms.validators import Optional

class Main_Memory():
	c0 = IntegerField('', validators=[Optional()])
	c1 = IntegerField('', validators=[Optional()])
	c2 = IntegerField('', validators=[Optional()])
	c3 = IntegerField('', validators=[Optional()])
	
	
