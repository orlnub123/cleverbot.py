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

Install it normally from `PyPI <https://pypi.org/project/cleverbot.py/>`_ with
pip:

::

    pip install cleverbot.py

Or install it with the asynchronous dependencies (Python 3.4.2+ only):

::

    pip install cleverbot.py[async]

**Requirements:**

- Python 3.1+ or 2.7
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

If you have the asynchronous dependencies and want to use Cleverbot
asynchronously import it as below instead:

.. code:: py

    from cleverbot import async_ as cleverbot

Then initialize Cleverbot with your API key and optionally a cleverbot state,
timeout and or tweak if you want to adjust Cleverbot's mood:

.. code:: py

    cb = cleverbot.Cleverbot('YOUR_API_KEY', cs='76nxdxIJ02AAA', timeout=60, tweak1=0, tweak2=100, tweak3=100)

The cleverbot state is the encoded state of the conversation that you get from
talking to Cleverbot and includes the whole conversation history.

If you're using Cleverbot asynchronously you can also give an event loop to
Cleverbot with a ``loop`` keyword argument

--------------

You can now start talking to Cleverbot.

Talk straight to Cleverbot:

.. code:: py

    reply = cb.say("Hello")

You can pass in keyword arguments to ``say`` such as ``cs`` to change the
conversation, ``vtext`` to change the current conversation's history, or even
``tweak`` as an alias for ``cb_settings_tweak`` to change Cleverbot's mood.
Read the "Parameters" section of `the official Cleverbot API docs
<https://www.cleverbot.com/api/howto/>`_ for more information.

Alternatively, start a new conversation and talk from it:

.. code:: py

    convo = cb.conversation()
    reply = convo.say("Hello")

Conversations are like mini Cleverbots so you can pass in anything that
Cleverbot takes as keyword arguments including ``key``. The values you don't
pass in excluding the cleverbot state will be taken from the originating
Cleverbot.

Normally conversations get saved in ``cb.conversations`` as a list but if you
want to manage them more easily you can pass in a name as the first argument to
every conversation you create which will turn ``cb.conversations`` into a
dictionary with the name as the key and the conversation as the value. Trying
to mix both named and nameless conversations will result in an error.

``say`` is a coroutine for both Cleverbot and its conversations if you're
running asynchronously.

--------------

If something goes wrong with the request such as an invalid API key an
``APIError`` will be raised containing the error message or if you've defined
a timeout and don't get a reply within the defined amount of seconds you'll
get a ``Timeout``.

As an example:

``cleverbot.errors.APIError: Missing or invalid API key or POST request, please
visit www.cleverbot.com/api``

You can get the error message and the HTTP status from the error
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

To access the data gained from talking straight to Cleverbot or from talking in
a conversation you can either get it from an attribute as shown previously or
directly get it from the ``data`` dictionary:

.. code:: py

    cb.conversation_id == cb.data['conversation_id']
    convo.conversation_id == convo.data['conversation_id']

Note that every attribute except for ``cs`` (i.e. the cleverbot state) is
read-only and will get shadowed if you set it to something.

For a list of all of the data and their descriptions go to the "JSON Reply"
section in `the official Cleverbot API docs
<https://www.cleverbot.com/api/howto/>`_.

To reset Cleverbot's and all of its conversations' data you can simply do the
following:

.. code:: py

    cb.reset()

To only reset a single conversation's data use ``reset`` on the conversation
instead:

.. code:: py

    convo.reset()

Resetting won't delete any conversations so you'll be able to reuse them.

--------------

If you want to save the current state of Cleverbot and all of its conversations
you can use ``cb.save``:

.. code:: py

    cb.save('cleverbot.pickle')

This saves the key, timeout and tweaks you've given to Cleverbot and its
conversations and also the current cleverbot state of each.

In order to load and recreate the previously saved state as a new Cleverbot
instance use ``cleverbot.load``:

.. code:: py

    cb = cleverbot.load('cleverbot.pickle')

To only load the conversations use ``cb.load``:

.. code:: py

    cb.load('cleverbot.pickle')

Loading conversations will delete the old ones.

--------------

When you're done with the current instance of Cleverbot, close Cleverbot's
connection to the API:

.. code:: py

    cb.close()
