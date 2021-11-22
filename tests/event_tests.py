import re
from django.http import request
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.authtoken.models import Token

from levelupapi.models import Event, Gamer, GameType, Game

class EventTests(APITestCase):
    def setUp(self):
        # TODO: Set up database with logged in user and game
        url = '/register'

        # Define the Gamer properties
        gamer = {
            "username": "steve",
            "password": "Admin8*",
            "email": "steve@stevebrownlee.com",
            "address": "100 Infinity Way",
            "phone_number": "555-1212",
            "first_name": "Steve",
            "last_name": "Brownlee",
            "bio": "Love those gamez!!"
        }

        # Initiate POST request and capture the response
        response = self.client.post(url, gamer, format='json')

        # Store the TOKEN from the response data
        self.token = Token.objects.get(pk=response.data['token'])

        # Use the TOKEN to authenticate the requests
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        game_type = GameType()
        game_type.label = "Board game"

        # Save the GameType to the testing database
        game_type.save()
        self.game = Game.objects.create(
            game_type=game_type,
            title="Monopoly",
            maker="Hasbro",
            gamer_id=1,
            number_of_players=5,
            skill_level=2
        )
        

    def test_retrieve(self):
        # TODO: Test the event retrieve method
        event = Event.objects.create(
            organizer_id=1,
            game=self.game,
            time="12:30:00",
            date="2021-12-23",
            description="Game night"
        )
        url = f'/events/{event.id}'
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], event.id)
        self.assertEqual(response.data['date'], event.date)
        self.assertEqual(response.data['time'], event.time)
        self.assertEqual(response.data['description'], event.description)
        self.assertEqual(response.data['organizer']['id'], event.organizer.id)

    def test_create(self):
        # TODO: Test the event create method
        event = {
            "date": "2021-12-23",
            "time": "12:30:00",
            "description": "Game Day",
            "gameId": self.game.id
        }
        response = self.client.post('/events', event, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['id'])
        self.assertEqual(response.data['date'], event['date'])
        self.assertEqual(response.data['time'], event['time'])
        self.assertEqual(response.data['description'], event['description'])
        self.assertEqual(response.data['organizer']['id'], 1)

    def test_delete(self):
        # TODO: Test the event delete method
        event = Event.objects.create(
            organizer_id=1,
            game=self.game,
            time="12:30:00",
            date="2021-12-23",
            description="Game night"
        )

        response = self.client.delete(f'/events/{event.id}')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        get_response = self.client.get(f'/events/{event.id}')
        self.assertEqual(get_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update(self):
        # TODO: Test the event update method
        event = Event.objects.create(
            organizer_id=1,
            game=self.game,
            time="12:30:00",
            date="2021-12-23",
            description="Game night"
        )

        event_dict = {
            'id': event.id,
            'gameId': event.game.id,
            'time': event.time,
            'date': "2021-12-27",
            'description': event.description
        }

        response = self.client.put(f'/events/{event.id}', event_dict, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        event_updated = Event.objects.get(pk=event.id)
        self.assertEqual(event_updated.date.strftime('%Y-%m-%d'), event_dict['date'])

    def test_joining_event(self):
        # TODO: Test joining an event method
        event = Event.objects.create(
            organizer_id=1,
            game=self.game,
            time="12:30:00",
            date="2021-12-23",
            description="Game night"
        )
        # Assert that no one is in the event list, the length should be 0
        self.assertEqual(len(event.attendees.all()), 0)

        response = self.client.post(f'/events/{event.id}/signup')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # After the post runs assert that the attendees length is 1
        self.assertEqual(len(event.attendees.all()), 1)

    def test_leaving_events(self):
        event = Event.objects.create(
            organizer_id=1,
            game=self.game,
            time="12:30:00",
            date="2021-12-23",
            description="Game night"
        )
        # Add a gamer to the attendees
        gamer = Gamer.objects.get(pk=1)
        event.attendees.add(gamer)

        response = self.client.delete(f'/events/{event.id}/signup')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(event.attendees.all()), 0)
