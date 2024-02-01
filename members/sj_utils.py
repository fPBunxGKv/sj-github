from .models import sj_events

from datetime import *
from escpos.printer import Network, Dummy


def print_paper(user_data, run_time=0, printer_ip='172.20.30.170', template='default'):
    print(f"Print-Templatename: { template }")
    # test if logo file is present
    
    # init dummy printer
    d = Dummy()

    if template == 'run':
        # Font, align, etc. settings
        print(f"set_widh_default")
        d.set_with_default(align='center', font='a', bold=True, underline=0, width=2, height=2, density=9, invert=False, smooth=False, flip=False, double_width=False, double_height=False, custom_size=False)
        print(f"set_1")
        d.set(align='center', font='a', bold=True, width=2, height=2, density=9, double_width=True, double_height=True)

        # create ESC/POS for the print job, this should go really fast
        # d.ln(3)
        # d.image("static/logo_211x211.png")
        # d.ln(3)

        d.textln(user_data.fk_sj_users.firstname)
        d.textln(user_data.fk_sj_users.lastname)

        print(f"set_2")
        d.set(align='center', font='a', bold=True, width=2, height=2, density=9, double_width=False, double_height=False)
        d.textln(user_data.result_category)
        d.ln(1)
        
        if run_time > 0:
            d.text(f"--  {run_time:2.2f}  --\n")
        else:
            d.text(f"--  ERROR  --\n")

        d.ln(2)
        d.barcode(str(user_data.fk_sj_users.startnum), 'CODE39', height=80, width=2, pos='BELOW', font='A', align_ct=True, function_type=None, check=True, force_software=False)
        d.cut()

    elif template == 'register':
        d.text(f"Template: {template}\n")
        d.ln(2)
        d.cut()

    else:
        d.text(f"Template: {template}\n")
        d.text(f"Definition fehlt...\n")
        d.ln(2)
        d.cut()

    # send code to printer
    try:
        p = Network(host=printer_ip, timeout=1)
        p._raw(d.output)
        return True
    
    except Exception as error:
        print("Printing error:", type(error).__name__, "-", error)
        return False


def is_valid_uuid(value):
    try:
        uuid.UUID(str(value))
        return True, uuid.UUID(str(value))
    except ValueError:
        return False, ''


def sendmail(state='na',firstmane='na',email='na', value=''):
    print("Will send Email for:", value, state, firstmane, email)



def get_event_info():
    active_event = sj_events.objects.filter(event_active=True).values('id','event_name','event_date','event_reg_start','event_reg_end','event_reg_open','event_num_lines').first()

    if active_event['event_reg_start'].date() <= datetime.now().date() <= active_event['event_reg_end'].date():
        reg_open = True
    else:
        reg_open = False

    return {
            "id": active_event['id'],
            "name": active_event['event_name'],
            "date": active_event['event_date'],
            "reg_open": reg_open,
            "lines": active_event['event_num_lines']
            }
