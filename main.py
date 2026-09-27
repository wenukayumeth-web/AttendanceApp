import mysql.connector
from mysql.connector import Error

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.properties import NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput

# Mobile 9:16 Aspect Ratio Window Size
Window.size = (360, 640)

# Cloud Database Credentials
CLOUD_DB_CONFIG = {
    'host': 'mysql-b6d282a-wenukayumeth-8cfa.k.aivencloud.com',
    'port': 25755,
    'user': 'avnadmin',
    'password': 'AVNS_MY8P76kaWEzbuv8BmEl',
    'database': 'defaultdb',
}


# --- HIGHLY TRANSPARENT GLASS CONTAINER ---
class NeonGlassCard(BoxLayout):
  glow_alpha = NumericProperty(0.4)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    with self.canvas.before:
      Color(0.02, 0.04, 0.08, 0.35)
      self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[22])

      self.glow_color = Color(0.0, 0.85, 1.0, self.glow_alpha)
      self.glow_line = Line(
          rounded_rectangle=(self.x, self.y, self.width, self.height, 22),
          width=1.5,
      )

    self.bind(pos=self._update_graphics, size=self._update_graphics)
    self.bind(glow_alpha=self._update_glow)
    self.start_glow_pulse()

  def _update_graphics(self, *args):
    self.rect.pos = self.pos
    self.rect.size = self.size
    self.glow_line.rounded_rectangle = (
        self.x,
        self.y,
        self.width,
        self.height,
        22,
    )

  def _update_glow(self, instance, value):
    self.glow_color.a = value

  def start_glow_pulse(self):
    anim = Animation(glow_alpha=0.9, d=1.8, t='in_out_quad') + Animation(
        glow_alpha=0.3, d=1.8, t='in_out_quad'
    )
    anim.repeat = True
    anim.start(self)


# --- TRANSPARENT TEXT INPUT WITH GLOW ---
class CustomTextInput(TextInput):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.background_normal = ''
    self.background_active = ''
    self.background_color = (0.0, 0.0, 0.0, 0.45)
    self.cursor_color = (0, 0.9, 1, 1)
    self.foreground_color = (1, 1, 1, 1)
    self.hint_text_color = (0.8, 0.9, 1.0, 0.6)
    self.font_size = '15sp'
    self.padding = [14, 12, 14, 12]

    with self.canvas.before:
      Color(0.0, 0.85, 1.0, 0.5)
      self.border_line = Line(
          rounded_rectangle=(self.x, self.y, self.width, self.height, 10),
          width=1.2,
      )

    self.bind(pos=self._update_border, size=self._update_border)

  def _update_border(self, *args):
    self.border_line.rounded_rectangle = (
        self.x,
        self.y,
        self.width,
        self.height,
        10,
    )

  def on_focus(self, instance, value):
    if value:
      anim = Animation(background_color=(0.0, 0.1, 0.25, 0.65), d=0.2)
      anim.start(self)
    else:
      anim = Animation(background_color=(0.0, 0.0, 0.0, 0.45), d=0.2)
      anim.start(self)


# --- FIXED COMPACT BUTTON ---
class CyberButton(Button):

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.background_normal = ''
    self.background_color = (0.0, 0.75, 0.95, 0.85)
    self.color = (1, 1, 1, 1)
    self.bold = True
    self.font_size = '14sp'

  def animate_click(self, callback=None):
    anim = Animation(height=38, d=0.08) + Animation(
        height=45, d=0.12, t='out_back'
    )
    if callback:
      anim.bind(on_complete=lambda a, w: callback())
    anim.start(self)


# --- MAIN APPLICATION WITH MULTI-IMAGE ANIMATED SLIDESHOW ---
class AttendanceApp(App):
  loading_dots = 0
  bg_index = 0

  bg_images = ['bg.jpg', 'bg1.jpg', 'bg2.jpg', 'bg3.jpg']

  def build(self):
    self.init_cloud_db()

    root = FloatLayout()

    # 1. Background Image Layer
    self.bg_image = Image(
        source=self.bg_images[0],
        allow_stretch=True,
        keep_ratio=False,
        size_hint=(1, 1),
        pos_hint={'x': 0, 'y': 0},
    )
    root.add_widget(self.bg_image)

    # 2. Main Neon Glass Card
    self.card = NeonGlassCard(
        orientation='vertical',
        padding=[22, 25, 22, 25],
        spacing=12,
        size_hint=(0.88, 0.75),
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
    )

    # Header Title
    self.header = Label(
        text=(
            '[b]CLOUD ATTENDANCE[/b]\n[size=12sp][color=00e5ff]✦ LIVE SYSTEM'
            ' ACTIVE ✦[/color][/size]'
        ),
        markup=True,
        font_size='20sp',
        halign='center',
        size_hint_y=None,
        height=55,
        color=(1, 1, 1, 1),
    )
    self.card.add_widget(self.header)

    # Status Label
    self.status_label = Label(
        text='[color=80deea]System Ready...[/color]',
        markup=True,
        font_size='12sp',
        size_hint_y=None,
        height=18,
    )
    self.card.add_widget(self.status_label)

    # Input 1: Teacher Name
    self.card.add_widget(
        Label(
            text='[color=ffffff][b]Teacher Name[/b][/color]',
            markup=True,
            size_hint_y=None,
            height=20,
            font_size='13sp',
        )
    )
    self.input_name = CustomTextInput(
        hint_text='Enter full name...',
        multiline=False,
        size_hint_y=None,
        height=45,
    )
    self.input_name.bind(text=self.on_typing)
    self.card.add_widget(self.input_name)

    # Input 2: Subject / Class
    self.card.add_widget(
        Label(
            text='[color=ffffff][b]Subject / Module[/b][/color]',
            markup=True,
            size_hint_y=None,
            height=20,
            font_size='13sp',
        )
    )
    self.input_subject = CustomTextInput(
        hint_text='Enter subject...',
        multiline=False,
        size_hint_y=None,
        height=45,
    )
    self.input_subject.bind(text=self.on_typing)
    self.card.add_widget(self.input_subject)

    self.card.add_widget(BoxLayout(size_hint_y=None, height=15))

    # Compact Submit Button
    self.submit_btn = CyberButton(
        text='SUBMIT ATTENDANCE', size_hint_y=None, height=45
    )
    self.submit_btn.bind(on_press=self.on_submit_click)
    self.card.add_widget(self.submit_btn)

    root.add_widget(self.card)

    self.animate_card_entrance()

    # Loop start
    Clock.schedule_interval(self.change_background_loop, 5.0)

    return root

  def change_background_loop(self, dt):
    self.bg_index = (self.bg_index + 1) % len(self.bg_images)
    next_image = self.bg_images[self.bg_index]

    fade_out = Animation(opacity=0, d=1.0, t='out_quad')

    def apply_next_bg(anim, widget):
      self.bg_image.source = next_image

      anim_type = self.bg_index % 3

      if anim_type == 0:
        self.bg_image.size_hint = (1.1, 1.1)
        self.bg_image.pos_hint = {'center_x': 0.5, 'center_y': 0.5}
        fade_in = Animation(opacity=1, size_hint=(1, 1), d=1.2, t='out_cubic')
      elif anim_type == 1:
        self.bg_image.size_hint = (1, 1)
        self.bg_image.pos_hint = {'x': 0, 'y': -0.05}
        fade_in = Animation(
            opacity=1, pos_hint={'x': 0, 'y': 0}, d=1.2, t='out_quad'
        )
      else:
        self.bg_image.size_hint = (1, 1)
        self.bg_image.pos_hint = {'x': 0, 'y': 0}
        # Fixed transition name: 'in_out_sine'
        fade_in = Animation(opacity=1, d=1.2, t='in_out_sine')

      fade_in.start(self.bg_image)

    fade_out.bind(on_complete=apply_next_bg)
    fade_out.start(self.bg_image)

  def animate_card_entrance(self):
    self.card.opacity = 0
    self.card.pos_hint = {'center_x': 0.5, 'center_y': 0.4}
    anim = Animation(
        opacity=1,
        pos_hint={'center_x': 0.5, 'center_y': 0.5},
        d=0.7,
        t='out_cubic',
    )
    anim.start(self.card)

  def on_typing(self, instance, value):
    if value:
      self.status_label.text = '[color=00e5ff] Typing in progress...[/color]'
    else:
      self.status_label.text = '[color=80deea]System Ready...[/color]'

  def on_submit_click(self, instance):
    self.submit_btn.animate_click(callback=self.start_submission)

  def start_submission(self):
    name = self.input_name.text.strip()
    subject = self.input_subject.text.strip()

    if not name or not subject:
      self.show_animated_popup(
          'Input Error', 'Please fill in all required fields!'
      )
      return

    self.submit_btn.disabled = True
    self.loading_dots = 0
    self.loading_event = Clock.schedule_interval(
        self.animate_loading_btn, 0.25
    )

    Clock.schedule_once(
        lambda dt: self.process_attendance(name, subject), 1.2
    )

  def animate_loading_btn(self, dt):
    self.loading_dots = (self.loading_dots % 3) + 1
    dots = '.' * self.loading_dots
    self.submit_btn.text = f'SUBMITTING {dots}'

  def process_attendance(self, name, subject):
    Clock.unschedule(self.loading_event)
    self.submit_btn.disabled = False
    self.submit_btn.text = 'SUBMIT ATTENDANCE'

    try:
      conn = mysql.connector.connect(**CLOUD_DB_CONFIG)
      cursor = conn.cursor()
      insert_query = (
          'INSERT INTO attendance_logs (teacher_name, subject) VALUES (%s, %s)'
      )
      cursor.execute(insert_query, (name, subject))
      conn.commit()
      cursor.close()
      conn.close()

      self.input_name.text = ''
      self.input_subject.text = ''
      self.status_label.text = (
          '[color=00e676]✓ Logged to Cloud Successfully![/color]'
      )
      self.show_animated_popup(
          'SUCCESS!', f'Attendance Logged Successfully for:\n[b]{name}[/b]'
      )

    except Error as e:
      self.show_animated_popup(
          'Cloud Error', f'Failed to sync with Database:\n{str(e)}'
      )

  def init_cloud_db(self):
    try:
      cloud_conn = mysql.connector.connect(**CLOUD_DB_CONFIG)
      cloud_cursor = cloud_conn.cursor()
      cloud_cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance_logs (
                    log_id INT AUTO_INCREMENT PRIMARY KEY,
                    teacher_name VARCHAR(100),
                    subject VARCHAR(100),
                    marked_date DATE DEFAULT (CURRENT_DATE)
                )
            """)
      cloud_conn.commit()
      cloud_cursor.close()
      cloud_conn.close()
    except Error as e:
      print(f'Cloud DB Warning: {e}')

  def show_animated_popup(self, title, message):
    popup_layout = BoxLayout(orientation='vertical', padding=20, spacing=15)
    popup_layout.add_widget(
        Label(
            text=message,
            markup=True,
            halign='center',
            font_size='14sp',
            color=(1, 1, 1, 1),
        )
    )

    close_btn = CyberButton(text='OK', size_hint_y=None, height=40)
    popup_layout.add_widget(close_btn)

    popup = Popup(
        title=title,
        content=popup_layout,
        size_hint=(0.82, 0.32),
        background_color=(0.05, 0.08, 0.15, 0.85),
        separator_color=(0, 0.85, 1, 0.8),
    )

    close_btn.bind(on_press=popup.dismiss)
    popup.open()


if __name__ == '__main__':
  AttendanceApp().run()