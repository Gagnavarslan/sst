import sst
import sst.actions
from sst import config


# PhantomJS can not do alerts by design
if config.browser_type == 'phantomjs':
    sst.actions.skip()


sst.actions.set_base_url('http://localhost:%s/' % sst.DEVSERVER_PORT)
sst.actions.go_to('/alerts')

# Accept an alert box and assert its text.
sst.actions.click_button('show-alert', wait=False)
sst.actions.accept_alert(u'JavaScript alert text')
sst.actions.assert_title('Page with JavaScript alerts')

# Accept a confirm box.
sst.actions.click_button('show-confirm', wait=False)
sst.actions.accept_alert()
sst.actions.accept_alert(u'Confirm accepted')

# Dismiss a confirm box and assert its text.
sst.actions.click_button('show-confirm', wait=False)
sst.actions.dismiss_alert(u'JavaScript confirm text')
sst.actions.accept_alert(u'Confirm dismissed')

# Enter text to a prompt box, accept it and assert its text.
sst.actions.click_button('show-prompt', wait=False)
sst.actions.accept_alert(u'JavaScript prompt text', 'Entered text')
sst.actions.accept_alert('Entered text')

# Enter text to a prompt box and dismiss it.
sst.actions.click_button('show-prompt', wait=False)
sst.actions.dismiss_alert(text_to_write='Entered text')
sst.actions.assert_title('Page with JavaScript alerts')
