#!/usr/bin/python
# -*- coding: utf-8 -*-
import json

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen

from kivy_communication import *
from text_handling.text_handling import *

import random


class ZeroScreen(Screen):
    pass


class EndScreen(Screen):
    pass


class QuestionScreen(Screen):
    current_question = 0
    next_question = 0
    the_text = None
    the_images = None
    exp_name = None

    def on_pre_enter(self, *args):
        self.update_question()

    def on_enter(self, *args):
        KL.log.insert(action=LogAction.data, obj='screen_question+' + str(self.current_question), comment='enter_screen')
        if self.the_text:
            TTS.speak([self.the_text])

    def update_question(self, current_question=None):
        image_sequence = [0, 1, 2, 3]
        random.shuffle(image_sequence)

        self.ids['A_button'].background_normal = 'images/' + str(self.the_images[image_sequence[0]])
        self.ids['B_button'].background_normal = 'images/' + str(self.the_images[image_sequence[1]])
        self.ids['C_button'].background_normal = 'images/' + str(self.the_images[image_sequence[2]])
        self.ids['D_button'].background_normal = 'images/' + str(self.the_images[image_sequence[3]])

        self.ids['A_button'].background_disabled_down = 'images/' + str(self.the_images[image_sequence[1]])
        self.ids['B_button'].background_disabled_down = 'images/' + str(self.the_images[image_sequence[2]])
        self.ids['C_button'].background_disabled_down = 'images/' + str(self.the_images[image_sequence[3]])
        self.ids['D_button'].background_disabled_down = 'images/' + str(self.the_images[image_sequence[0]])

        # because log goes after this, the name is changed to (real number - 1)
        self.ids['A_button'].name = str(self.current_question) + '_A_' + self.the_images[image_sequence[0]][:-4] + '_' + str(image_sequence[0])
        self.ids['B_button'].name = str(self.current_question) + '_B_' + self.the_images[image_sequence[1]][:-4] + '_' + str(image_sequence[1])
        self.ids['C_button'].name = str(self.current_question) + '_C_' + self.the_images[image_sequence[2]][:-4] + '_' + str(image_sequence[2])
        self.ids['D_button'].name = str(self.current_question) + '_D_' + self.the_images[image_sequence[3]][:-4] + '_' + str(image_sequence[3])

    def pressed(self, answer):
        print(answer)
        if self.next_question > 0:
            next_screen = 'question_screen_' + str(self.next_question).zfill(2)
            self.manager.current = next_screen
        else:
            self.manager.current = 'end_screen'


class PpvtLikeApp(App):
    q_dict = {}

    def build(self):
        self.load_questions()
        self.init_communication()

        TTS.start()
        self.sm = ScreenManager()

        self.zero_screen = ZeroScreen(name='zero_screen')
        self.zero_screen.ids['subject_id'].bind(text=self.zero_screen.ids['subject_id'].on_text_change)
        self.sm.add_widget(self.zero_screen)

        self.questions = []
        i_question = 0
        for exp_name, questions in self.q_dict.items():
            for q_number, q_data in questions.items():
                self.questions.append(QuestionScreen(name='question_screen_' + str(i_question).zfill(2)))
                self.questions[-1].exp_name = exp_name
                self.questions[-1].the_text = q_data['text']
                self.questions[-1].the_images = q_data['images']
                self.questions[-1].current_question = int(q_number)
                if self.questions[-1].current_question < len(questions):
                    self.questions[-1].next_question = i_question + 1
                else:
                    self.questions[-1].next_question = -1
                i_question += 1

        random.shuffle(self.questions)
        for q_screen in self.questions:
            self.sm.add_widget(q_screen)

        self.end_screen = EndScreen(name='end_screen')
        self.sm.add_widget(self.end_screen)

        self.sm.current = 'zero_screen'
        return self.sm

    def load_questions(self):
        self.q_dict = json.load(open('images/questions.json'))

    def init_communication(self):
        KC.start(the_ip='192.168.1.254', the_parents=[self])  # 127.0.0.1
        KL.start(mode=[DataMode.file, DataMode.communication, DataMode.ros], pathname=self.user_data_dir,
                 the_ip='192.168.1.254')

    def on_connection(self):
        KL.log.insert(action=LogAction.data, obj='SpatialSkillAssessmentApp', comment='start')

    def press_start(self, current_question):
        self.sm.current = 'question_screen_' + str(current_question).zfill(2)

    def end_game(self):
        self.stop()

if __name__ == '__main__':
    PpvtLikeApp().run()
