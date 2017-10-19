cleverbot.py
============

cleverbot.py is a Cleverbot API wrapper for Python made to be both
fully-featured and easy to use.

Example
-------

.. code:: py

    import cleverbot


    cb = cleverbot.Cleverbot('YOUR_API_KEY', timeout=60)

    text = input("Say to Cleverbot: ")
    try:
        reply = cb.say(text)
    except cleverbot.CleverbotError as error:
        print(error)
    else:
        print(reply)
    finally:
        cb.close()

Installing
----------

Install it normally from PyPI with pip:

::

    pip install cleverbot.py

Or install it with the asynchronous dependencies (Python 3.4.2+ only):

::

    pip install cleverbot.py[async]

**Requirements:**

- Python 3.2+ or 2.6+
- `A Cleverbot API key <https://www.cleverbot.com/api/>`_

**Dependencies:**

- requests 1.0.0+

+ **Asynchronous:**

  - aiohttp 1.0.0+

Usage
-----

First import the package:

.. code:: py

    import cleverbot

Then initialize Cleverbot with your API key and optionally a cleverbot state
and or timeout:

.. code:: py

    cb = cleverbot.Cleverbot('YOUR_API_KEY', cs='76nxdxIJ02AAA', timeout=60)

The cleverbot state is the encoded state of the conversation that you get from
talking to Cleverbot and includes the whole conversation history.

If you have the asynchronous dependencies and want to use Cleverbot
asynchronously import ``cleverbot.async_`` and initialize Cleverbot from
``cleverbot.async_.Cleverbot`` instead. The only differences are that ``say``
is a coroutine and that you can pass an event loop to Cleverbot with a ``loop``
keyword argument.

--------------

You can now start talking to Cleverbot.

Get the reply from the request:

.. code:: py

    reply = cb.say("Hello")

Or alternatively get it later:

.. code:: py

    cb.say("Hello")
    reply = cb.output

You can also pass in keyword arguments such as ``cs`` to change the
conversation, or ``vtext`` to change the current conversation's history. Read
the "Parameters" section of `the official Cleverbot API docs
<https://www.cleverbot.com/api/howto/>`_ for more information.

--------------

If something goes wrong with the request, such as an invalid API key, an
``APIError`` will be raised containing the error message or, if you've defined
a timeout and you don't get a reply within the defined amount of seconds you'll
get a ``Timeout``.

As an example:

``cleverbot.errors.APIError: Missing or invalid API key or POST request, please
visit www.cleverbot.com/api``

You can get the error message and additionally the HTTP status from the error
like so:

.. code:: py

    try:
        cb.say("Hello")
    except cleverbot.APIError as error:
        print(error.error, error.status)

This is similar for ``Timeout`` where you can get the defined timeout
value with ``error.timeout``.

Additionally, all Cleverbot errors subclass ``CleverbotError`` so you can use
it to catch every Cleverbot related error.

--------------

To access the data gained from the conversations you can either get them from
an attribute as shown previously or directly get them from ``cb.data``:

.. code:: py

    cb.conversation_id == cb.data['conversation_id']

However modifying the data with an attribute is only applicable to the
cleverbot state by using the ``cs`` attribute.

For a list of all of the data's items' descriptions go to the "JSON Reply"
section in `the official Cleverbot API docs
<https://www.cleverbot.com/api/howto/>`_.

To reset the data you can simply do the following:

.. code:: py

    cb.reset()

--------------

When you're done with the current instance of Cleverbot, close Cleverbot's
connection to the API:

.. code:: py

    cb.close()
