Create a service to manage alerts for products prices on Ebay.com, the service will allow a user
to create an alert so he can receive updates about specific products search phrases delivered to
his email address.

Through this solution a user can create an alert by providing a search phrase, email address and
one of the values (2 minutes, 10 minute or 30 minutes) that specify how often he will receive the
updates.

User should obtain the first 20 products sorted by the lowest price every 2, 10 or 30 minutes
delivered to his email address as per alert configuration.

Several alerts can be created for the same email address but with different search phrases.

● Create all CRUD operations.

● Add a simple UI (preferred in reactjs) to create new alerts and show available alerts (this is
optional).

● Authentication is not required.

● The solution should work locally using: docker-compose up

● Add tests whenever possible.

● Expose the documentation of the api with swagger or in the readme file, also provide a
short explanation for your architecture and design decisions.

● Provide documentation about project setup, run tests and run the solution locally.

Hint: create a client app in eBay from this link [https://developer.ebay.com](https://developer.ebay.com) to obtain the App ID,
you can use the searching api.