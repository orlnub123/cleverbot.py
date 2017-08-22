cleverbot.py
============

cleverbot.py is a Cleverbot API wrapper for Python made to be both
fully-featured and easy to use.

Installing
----------

Install it from PyPI using pip:

::

    pip install cleverbot.py

Or install it from GitHub with git:

::

    git clone https://github.com/orlnub123/cleverbot.py
    cd cleverbot.py
    python setup.py install

If you don't have pip or git you can also download the source and run ``python
setup.py install`` on it.

**Requirements:**

- Python 3.2+ or 2.6+
- `A Cleverbot API key <http://www.cleverbot.com/api/>`_

**Dependencies:**

- Requests 1.0.0+

Usage
-----

First import the module.

.. code:: py

    import cleverbot

--------------

Then initialize Cleverbot with your API key and optionally a cleverbot
state and or timeout.

.. code:: py

    cb = cleverbot.Cleverbot('YOUR_API_KEY', cs='76nxdxIJ02AAA', timeout=60)

The cleverbot state is the encoded state of the conversation so far and
includes the whole conversation history up to that point.

--------------

You can now start talking to Cleverbot.

Get the reply from the input:

.. code:: py

    reply = cb.say("Hello")

Or alternatively get it later:

.. code:: py

    cb.say("Hello")
    reply = cb.output

--------------

If something goes wrong with the request, such as an invalid API key an
``APIError`` will be raised containing the error message and HTTP status
code or, if you've defined a timeout and the request times out you'll
get a ``Timeout``.

As an example:

``cleverbot.errors.APIError: Missing or invalid API key or POST request, please
visit www.cleverbot.com/api Status: 401``

Also, all Cleverbot errors subclass ``CleverbotError`` so you can use it
to catch everything Cleverbot related.

--------------

Print out all of the attributes Cleverbot gained from the previous
conversation.

.. code:: py

    print(cb.attr_list)

Take note of the ``cs`` attribute as we'll use it to save the conversation in
the next section.

To get a list of all of the attributes' descriptions either take a look at the
``query`` function's docstring in cleverbot.py or go to the JSON Reply section
at `the official Cleverbot API docs <https://www.cleverbot.com/api/howto/>`_.

--------------

Save the conversation in preparation for a reset.

.. code:: py

    cs = cb.cs

Reset Cleverbot, deleting all of its attributes gained from the previous
conversations.

.. code:: py

    cb.reset()

Note that if you try to get the cleverbot state now you'll get an error:

``AttributeError: 'Cleverbot' object has no attribute 'cs'``

Now start right where you left off by setting the cleverbot state you saved
earlier.

.. code:: py

    cb.cs = cs

Or by setting it when creating a new Cleverbot instance.

.. code:: py

    cb = cleverbot.Cleverbot('YOUR_API_KEY', cs=cs)

--------------

If you wish to use ``cleverbot`` as a variable you can do one of the following:

.. code:: py

    import cleverbot as some_other_name

.. code:: py

    from cleverbot import *

--------------

Example
~~~~~~~

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
