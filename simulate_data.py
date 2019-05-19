from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import Required, Optional

class Simulate(FlaskForm):
	data = StringField('Input reference list: ', validators=[Required()])
	
	cache_0 = StringField('', validators=[Optional()])
	cache_1 = StringField('', validators=[Optional()])
	cache_2 = StringField('', validators=[Optional()])
	cache_3 = StringField('', validators=[Optional()])

	tlb0page = StringField('', validators=[Optional()])
	tlb0offset = StringField('', validators=[Optional()])
	tlb1page = StringField('', validators=[Optional()])
	tlb1offset = StringField('', validators=[Optional()])
	
	frame0 = StringField('', validators=[Optional()])
	frame1 = StringField('', validators=[Optional()])
	frame2 = StringField('', validators=[Optional()])
	frame3 = StringField('', validators=[Optional()])
	frame4 = StringField('', validators=[Optional()])
	frame5 = StringField('', validators=[Optional()])
	frame6 = StringField('', validators=[Optional()])
	frame7 = StringField('', validators=[Optional()])
	
	page0frm = StringField('', validators=[Optional()])
	page1frm = StringField('', validators=[Optional()])
	page2frm = StringField('', validators=[Optional()])
	page3frm = StringField('', validators=[Optional()])
	page4frm = StringField('', validators=[Optional()])
	page5frm = StringField('', validators=[Optional()])
	page6frm = StringField('', validators=[Optional()])
	page7frm = StringField('', validators=[Optional()])
	

	
			
	