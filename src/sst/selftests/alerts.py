from sst.actions import *
from sst import config

# PhantomJS can not do alerts by design
if config.browser_type == 'phantomjs':
    skip()

go_to('/alerts')

# Accept an alert box and assert its text.
click_button('show-alert', wait=False)
accept_alert(u'JavaScript alert text')
assert_title('Page with JavaScript alerts')

# Accept a confirm box.
click_button('show-confirm', wait=False)
accept_alert()
accept_alert(u'Confirm accepted')

# Dismiss a confirm box and assert its text.
click_button('show-confirm', wait=False)
dismiss_alert(u'JavaScript confirm text')
accept_alert(u'Confirm dismissed')

# Enter text to a prompt box, accept it and assert its text.
click_button('show-prompt', wait=False)
accept_alert(u'JavaScript prompt text', 'Entered text')
accept_alert('Entered text')

# Enter text to a prompt box and dismiss it.
click_button('show-prompt', wait=False)
dismiss_alert(text_to_write='Entered text')
assert_title('Page with JavaScript alerts')
