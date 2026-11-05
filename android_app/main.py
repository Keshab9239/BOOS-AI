from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button

class BOOSApp(App):
    def build(self):
        layout = BoxLayout(orientation="vertical", padding=15, spacing=10)

        title = Label(
            text="BOOS AI",
            font_size=30,
            size_hint_y=0.2
        )

        self.chat = Label(
            text="Namaste! Main BOOS hoon. Aapki kya madad kar sakta hoon?",
            halign="left",
            valign="top"
        )
        self.chat.bind(size=self.chat.setter("text_size"))

        self.message = TextInput(
            hint_text="Yahan apna message likho...",
            multiline=False,
            size_hint_y=0.15
        )

        send = Button(text="SEND", size_hint_y=0.15)
        send.bind(on_press=self.send_message)

        layout.add_widget(title)
        layout.add_widget(self.chat)
        layout.add_widget(self.message)
        layout.add_widget(send)

        return layout

    def send_message(self, instance):
        text = self.message.text.strip()
        if text:
            self.chat.text = "Aap: " + text + "\n\nBOOS: App ka AI connection agle step mein jodega."
            self.message.text = ""

BOOSApp().run()
