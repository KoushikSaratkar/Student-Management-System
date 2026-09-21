import tkinter as tk
from tkinter.ttk import Combobox,Treeview
from tkinter.filedialog import askopenfilename,askdirectory
from PIL import Image,ImageTk,ImageDraw,ImageFont,ImageOps
from io import BytesIO
import re
import random
import sqlite3
import os
import win32api
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import my_email
from tkinter.scrolledtext import ScrolledText
import threading




root = tk.Tk()
root.geometry("500x600")
root.title("Student Management System")

bg_color='#273b7a'

# Images
login_student_icon = tk.PhotoImage(file=r'Images\login_student_img.png')
login_admin_icon = tk.PhotoImage(file=r'Images\admin_img.png')
add_student_icon = tk.PhotoImage(file=r'Images\add_student_img.png')
locked_icon = tk.PhotoImage(file=r'Images\locked.png')
unlocked_icon = tk.PhotoImage(file=r'Images\unlocked.png')
add_student_pic_icon = tk.PhotoImage(file=r'Images\add_image.png')



# Connect Database or Fetch the Data
def init_database():

    if os.path.exists('students_accounts.db'):
        connection = sqlite3.connect('students_accounts.db')
        cursor = connection.cursor()
        cursor.execute("""
        SELECT * FROM data
        """)
        
        connection.commit()
        # print(cursor.fetchall())
        connection.close()
        
    else:

        # Create Database
        connection = sqlite3.connect('students_accounts.db')
        cursor = connection.cursor()
        cursor.execute("""
        CREATE TABLE data(
        id_number text,
        password text,
        name text,
        age text,
        gender text,
        phone_number text,
        class text,
        email text,
        image blob
        )
        """)

        connection.commit()
        connection.close()

# Check ID is Already Exists
def check_id_already_exists(id_number):
    connection=sqlite3.connect('students_accounts.db')
    cursor = connection.cursor()

    cursor.execute(f"""
            SELECT id_number FROM data WHERE id_number == '{id_number}'
            """)

    connection.commit()
    response = cursor.fetchall()
    connection.close()

    return response

# Check the password is Correct or Not
def check_valid_password(id_number, password):
    connection=sqlite3.connect('students_accounts.db')
    cursor = connection.cursor()

    cursor.execute(f"""
            SELECT id_number,password FROM data WHERE id_number == '{id_number}' AND password == '{password}'
            """)

    connection.commit()
    response = cursor.fetchall()
    connection.close()

    return response


# Add Data Into Database
def add_data(id_number, password, name, age, gender, phone_number, 
             student_class, email, pic_data):

    connection = sqlite3.connect('students_accounts.db')
    cursor = connection.cursor()
    cursor.execute(f"""
            INSERT INTO data VALUES('{id_number}','{password}','{name}','{age}','{gender}',
            '{phone_number}','{student_class}','{email}',?)
            """,[pic_data])
    
    connection.commit()
    connection.close()


####### Confirmation Box
def confirmation_box(message):

    # confirmation  Frame not cancel or cancel
    answer = tk.BooleanVar()
    answer.set(False)

    def action(ans):
        answer.set(ans)
        confirmation_box_fm.destroy()

    # Confirmation Box Frame
    confirmation_box_fm = tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)

    # Message Label
    message_lb = tk.Label(confirmation_box_fm,text=message,font=('Bold',15))
    message_lb.pack(pady=20)

    # Cancel Btn
    cancel_btn = tk.Button(confirmation_box_fm,text='Cancel',font=('Bold',15),
                           bd=0,bg=bg_color,fg='white',
                           command=lambda:action(False))
    cancel_btn.place(x=50,y=160)

    # Yes Btn
    yes_btn = tk.Button(confirmation_box_fm,text='Yes',font=('Bold',15),
                            bd=0,bg=bg_color,fg='white',
                            command=lambda:action(True))
    yes_btn.place(x=190,y=160,width=80)

    confirmation_box_fm.place(x=100,y=120,width=320,height=220)

    root.wait_window(confirmation_box_fm)
    return answer.get()


######### Message Box 
def message_box(message):

    # Message Box Frame
    message_box_fm = tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)


    #  Message Close Button 
    close_btn = tk.Button(message_box_fm,text='X',bd=0,font=('Bold',13),
                          fg=bg_color,command=lambda:message_box_fm.destroy())
    close_btn.place(x=320,y=5)

    # Message Label
    message_lb = tk.Label(message_box_fm,text=message,font=('Bold',15))
    message_lb.pack(pady=50)

    message_box_fm.place(x=100,y=120,width=350,height=200)


# Drawwing Student Card 
def draw_student_card(student_pic_path,student_data):

   # Student details
    labels = """ID Number:
Name:
Gender:
Age:
Class:
Contact:
Email:
"""

    # Open student card template
    student_card = Image.open(r'Images\student_card_frame.png').convert('RGB')

    # Open student image
    pic = Image.open(student_pic_path).resize((80,80))

    
    

    # Paste student photo
    student_card.paste(pic, (15, 25))

    # Draw text
    draw = ImageDraw.Draw(student_card)

    heading_font = ImageFont.truetype('bahnschrift', 18)
    labels_font = ImageFont.truetype('arial', 12)

    # Heading
    draw.text(
        xy=(105, 35),
        text='Student Card',
        fill=(0, 0, 0),
        font=heading_font
    )

    draw.multiline_text(
        xy=(15, 120),
        text=labels,
        fill=(0, 0, 0),
        font=labels_font,
        spacing=6
    )

    draw.multiline_text(
            xy=(95, 104),
            text=student_data,
            fill=(0, 0, 0),
            font=labels_font,
            spacing=6
        )

    # Show card
    return student_card




# Student Card Student 
def student_card_page(student_card_obj, bypass_login_page=False):

    # Save Student Card
    def save_student_card():
        path = askdirectory()

        if path:
            print(path)

            student_card_obj.save(f'{path}/student_card.png')

    # Print Student Card
    def print_student_card():
        path = askdirectory()
        
        if path:
            print(path)
        
            student_card_obj.save(f'{path}/student_card.png')

            win32api.ShellExecute(0, 'print', f'{path}/student_card.png',
                                  None, '.',0)
            
    # For When you Close The Student Card you go back to login page
    def close_page():
        student_card_page_fm.destroy()

        if not bypass_login_page:
            root.update()
            student_login_page()



    student_card_img = ImageTk.PhotoImage(student_card_obj)

    # Frame
    student_card_page_fm = tk.Frame(root,highlightbackground=bg_color,
                                    highlightthickness=3)
    
    # Frame Heading
    heading_lb=tk.Label(student_card_page_fm,text="Student Card",
                            bg=bg_color,fg='white',font=('Bold',18))
    heading_lb.place(x=0,y=0,width=400)

    # Close Button on Frame 
    close_btn = tk.Button(student_card_page_fm, text='X', bg=bg_color,
                          fg='white', font=('Bold',13),bd=0,
                          command=close_page)
    
    close_btn.place(x=370, y=0)

  

    student_card_lb = tk.Label(student_card_page_fm, image=student_card_img)
    student_card_lb.place(x=50,y=50)

    student_card_lb.image = student_card_img

 

    # Save Button on Student Card Frame 
    save_student_card_btn = tk.Button(student_card_page_fm, text='Save Student Card',
                                      bg=bg_color, fg='white', font=('Bold',15),
                                      bd=1, command=save_student_card)
    save_student_card_btn.place(x=80,y=375)

    # Print Button on Student Card Frame 
    print_student_card_btn = tk.Button(student_card_page_fm, text='🖨️',
                                          bg=bg_color, fg='white', font=('Bold',18),
                                          bd=1,command=print_student_card)
    print_student_card_btn.place(x=270,y=370)

#///////////////////////////////////////////////////////////////////////
    student_card_page_fm.place(x=50, y=30, width=400, height=450)


############# Welcome Page
def welcome_page():

    # Forward to Student Login Page
    def forward_to_student_login_page():
        welcome_page_fm.destroy()
        root.update()
        student_login_page()

    # Forward to Admin Login page
    def forward_to_admin_login_page():
        welcome_page_fm.destroy()
        root.update()
        admin_login_page()

    # Forward to Create Account Page
    def forward_to_create_account_page():
        welcome_page_fm.destroy()
        root.update()
        add_account_page()


    ##### Frame
    welcome_page_fm=tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)

    # Frame Heading
    heading_lb=tk.Label(welcome_page_fm,text="Welcome To Student Registration\n&& Management System",
                        bg=bg_color,fg='white',font=('Bold',18))
    heading_lb.place(x=0,y=0,width=400)

    
    # All  Things Inside  Frame

    # Student Login
    student_login_btn = tk.Button(welcome_page_fm,text="Login Student",bg=bg_color,
                                fg='white',font=('Bold',15),bd=0,
                                command=forward_to_student_login_page)
    student_login_btn.place(x=120,y=125,width=200)

    student_login_img = tk.Button(welcome_page_fm,image=login_student_icon,bd=0,
                                  command=forward_to_student_login_page)
    student_login_img.place(x=60,y=100)


    # Admin Login
    admin_login_btn = tk.Button(welcome_page_fm,text="Login Admin",bg=bg_color,
                                fg='white',font=('Bold',15),bd=0,
                                command=forward_to_admin_login_page)
    admin_login_btn.place(x=120,y=225,width=200)

    admin_login_img = tk.Button(welcome_page_fm,image=login_admin_icon,bd=0,
                                command=forward_to_admin_login_page)
    admin_login_img.place(x=60,y=200)


    # Add Student
    add_student_btn = tk.Button(welcome_page_fm,text="Create Account",bg=bg_color,
                                fg='white',font=('Bold',15),bd=0,
                                command=forward_to_create_account_page)
    add_student_btn.place(x=120,y=325,width=200)

    add_student_img = tk.Button(welcome_page_fm,image=add_student_icon,bd=0,
                                command=forward_to_create_account_page)
    add_student_img.place(x=60,y=300)

#////////////////////////////////////////////////////////////////////
    welcome_page_fm.pack(pady=30)
    welcome_page_fm.pack_propagate(False)
    welcome_page_fm.configure(width=400,height=420)


# Sead Mail To Student About Information
def seadmail_to_student(email, message, subject):

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587

    username = my_email.email_address
    password = my_email.password

    msg = MIMEMultipart()

    msg['Subject'] = subject
    msg['From'] = username
    msg['To'] = email

    msg.attach(MIMEText(_text=message,_subtype='html'))

    smtp_connection = smtplib.SMTP(host=smtp_server, port=smtp_port)
    smtp_connection.starttls()
    smtp_connection.login(user=username,password=password)


    smtp_connection.sendmail(from_addr=username,to_addrs=email,msg=msg.as_string())
    # print('Mail Sent Successfully')

    smtp_connection.quit()



# Forget Password and Recover the Password 
def forget_password_page():

    # Recover a Password from the database
    def recover_password():

        if check_id_already_exists(id_number=student_id_ent.get()):
            print('correct ID')

            # Made a connection with database
            connection = sqlite3.connect('students_accounts.db')
            cursor = connection.cursor()

            cursor.execute(f"""
            SELECT password FROM data WHERE id_number == '{student_id_ent.get()}'
            """)

            connection.commit()
            recovered_password = cursor.fetchall()[0][0]
            

            cursor.execute(f"""
            SELECT email FROM data WHERE id_number == '{student_id_ent.get()}'
            """)

            connection.commit()
            student_email = cursor.fetchall()[0][0]
            connection.close()

            confirmation = confirmation_box(message=f"""We will Sent\nYour Forget Password
Via Your Email Address:
{student_email}
Do You Want To Continue
""")
            if confirmation:
                msg = f"""<h1> Your Forget Password is:</h1>
                <h2>{recovered_password}</h2>
                <p>Once Remember Your Password, After Delete This Message</p> """
                seadmail_to_student(email=student_email,message=msg,
                                    subject='Password Recovery')


        else:
            print('incorrect ID')
            message_box(message='! Invalid ID Number')




    # Create a frame
    forget_password_page_fm = tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)


    # Create a Label
    heading_lb=tk.Label(forget_password_page_fm,text="⚠️ Forget Password",
                                bg=bg_color,fg='white',font=('Bold',18))
    heading_lb.place(x=0,y=0,width=350)

    # Close Button
    close_btn = tk.Button(forget_password_page_fm,text='X',
                          font=('Bold',13),bg=bg_color,fg='white',
                          bd=0, command=lambda:forget_password_page_fm.destroy())
    close_btn.place(x=320,y=0)

    # Student ID Label and Entry Box
    student_id_lb = tk.Label(forget_password_page_fm,text='Enter Student ID Number',
                             font=('Bold',13))
    student_id_lb.place(x=70,y=40)

    # Entry Box
    student_id_ent = tk.Entry(forget_password_page_fm,
                              font=('Bold',15),justify=tk.CENTER)
    student_id_ent.place(x=70,y=70,width=180)

    # Information Label
    info_lb = tk.Label(forget_password_page_fm, text="""Via Your Email Address
We Will Send to You 
Your Forget Password.
""",justify=tk.LEFT)
    info_lb.place(x=75, y=110)


    # Next Button
    next_btn = tk.Button(forget_password_page_fm,
                         text='Next', font=('Bold',13),bg=bg_color,
                         fg='white',command=recover_password)
    next_btn.place(x=130,y=200,width=80)

#//////////////////////////////////////////////////////////////////////
    forget_password_page_fm.place(x=75,y=120, width=350, height=250)

# Fetching the data from the database
def fetch_student_data(query):
    connection = sqlite3.connect('students_accounts.db')
    cursor = connection.cursor()
    cursor.execute(query)
    connection.commit()
    response = cursor.fetchall()
    connection.close()
    return response



# Create a Student Dashboard
def student_dashborad(student_id):

    get_student_details = fetch_student_data(f"""
    SELECT name, age, gender, class, phone_number, email 
    FROM data 
    where id_number =='{student_id}'
    """)

    get_student_pic = fetch_student_data(f"""
        SELECT image 
        FROM data 
        where id_number == '{student_id}'
    """)

    student_pic = BytesIO(get_student_pic[0][0])

    # For Logout from Account
    def logout():

        confirm = confirmation_box(message='Do you Want to\nLogout Your Account?')

        if confirm:
            dashboard_fm.destroy()
            welcome_page()
            root.update()

    # for switch a indicator colour
    def switch(indicator,page):
        home_btn_indicator.config(bg='#c3c3c3')
        student_card_btn_indicator.config(bg='#c3c3c3')
        security_btn_indicator.config(bg='#c3c3c3')
        edit_data_btn_indicator.config(bg='#c3c3c3')
        delete_btn_indicator.config(bg='#c3c3c3')

        indicator.config(bg=bg_color)

        for child in page_fm.winfo_children():
            child.destroy()
            root.update()

        page()

    # Dashboard Frame
    dashboard_fm = tk.Frame(root,highlightbackground=bg_color,
                            highlightthickness=3)
    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.configure(width=480,height=580)

    # Option Frame
    options_fm = tk.Frame(dashboard_fm,highlightbackground=bg_color,
                            highlightthickness=2,bg='#c3c3c3')

    options_fm.place(x=0, y=0, width=120,height=575)

    # Home Button
    home_btn = tk.Button(options_fm,text='Home',font=('Bold',15),
                         fg=bg_color,bg='#c3c3c3',bd=0,
                         command=lambda:
                        switch(indicator=home_btn_indicator,
                                page=home_page))
    home_btn.place(x=10,y=50)

    # Home Button Side Label
    home_btn_indicator = tk.Label(options_fm, bg=bg_color,
                                  )
    home_btn_indicator.place(x=5,y=48,width=3,height=40)

    # Student Card Button
    student_card_btn = tk.Button(options_fm,text='Student\nCard',font=('Bold',15),
                             fg=bg_color,bg='#c3c3c3',bd=0,justify=tk.LEFT,
                             command=lambda:
                             switch(indicator=student_card_btn_indicator,
                                    page=dashboard_student_card_page))
    student_card_btn.place(x=10,y=100)

    # Student Card Button Side Label
    student_card_btn_indicator = tk.Label(options_fm, bg='#c3c3c3')
    student_card_btn_indicator.place(x=5,y=108,width=3,height=40)

    # Security Button
    security_btn = tk.Button(options_fm,text='Security',font=('Bold',15),
                             fg=bg_color,bg='#c3c3c3',bd=0,
                             command=lambda:
                             switch(indicator=security_btn_indicator,
                                    page=security_page))
    security_btn.place(x=10,y=170)

    # Security Button Side Label
    security_btn_indicator = tk.Label(options_fm, bg='#c3c3c3')
    security_btn_indicator.place(x=5,y=170,width=3,height=40)

    # Edit Data
    edit_data_btn = tk.Button(options_fm,text='Edit Data',font=('Bold',15),
                             fg=bg_color,bg='#c3c3c3',bd=0,
                             command=lambda:
                             switch(indicator=edit_data_btn_indicator,
                                    page=edit_data_page))
    edit_data_btn.place(x=10,y=220)

    # Edit Data Button Side Label
    edit_data_btn_indicator = tk.Label(options_fm, bg='#c3c3c3')
    edit_data_btn_indicator.place(x=5,y=220,width=3,height=40)

    # Delete Button
    delete_account_btn = tk.Button(options_fm,text='Delete\nAccount',font=('Bold',15),
                             fg=bg_color,bg='#c3c3c3',bd=0,justify=tk.LEFT,
                             command=lambda:
                             switch(indicator=delete_btn_indicator,
                                    page=delete_page))
    delete_account_btn.place(x=10,y=270)

    # Delete Button Side Label
    delete_btn_indicator = tk.Label(options_fm, bg='#c3c3c3')
    delete_btn_indicator.place(x=5,y=280,width=3,height=40)

    # Logout Button
    logout_btn = tk.Button(options_fm,text='Logout',font=('Bold',15),
                             fg=bg_color,bg='#c3c3c3',bd=0,command=logout)
    logout_btn.place(x=10,y=340)

    # logout_btn_indicator = tk.Label(options_fm, bg=bg_color)
    # logout_btn_indicator.place(x=5,y=340,width=3,height=40)

    # create a  Home page Frame inside dashborad frame 
    def home_page():

        student_pic_image_obj =Image.open(student_pic)
        size = 100
        mask = Image.new(mode='L',size=(size,size))

        draw_circle = ImageDraw.Draw(im=mask)
        draw_circle.ellipse(xy=(0,0,size,size),fill=255)

        output = ImageOps.fit(image=student_pic_image_obj,size=mask.size,
                              centering=(1,1))
        output.putalpha(mask)

        student_picture = ImageTk.PhotoImage(output)

        home_page_fm = tk.Frame(page_fm)
        home_page_fm.pack(fill=tk.BOTH,expand=True)

        student_pic_lb = tk.Label(home_page_fm, image=student_picture)
        student_pic_lb.image = student_picture
        student_pic_lb.place(x=10,y=10)

        hi_lb = tk.Label(home_page_fm, text=f'!Hi {get_student_details[0][0]}',
                         font=('Bold',15))
        hi_lb.place(x=130,y=50)

        student_details =f"""
    Student ID: {student_id}\n
    Name: {get_student_details[0][0]}\n
    Age: {get_student_details[0][1]}\n
    Gender: {get_student_details[0][2]}\n
    Class: {get_student_details[0][3]}\n
    Contact: {get_student_details[0][4]}\n
    Email: {get_student_details[0][5]}\n
    """ 
        student_details_lb =tk.Label(home_page_fm,text=student_details,
                                     font=('Bold',13),justify=tk.LEFT)
        student_details_lb.place(x=20,y=130)


    # Create a Student Card inside dashboard frame
    def dashboard_student_card_page():

        student_details = f"""
    {student_id}
    {get_student_details[0][0]}
    {get_student_details[0][2]}
    {get_student_details[0][1]}
    {get_student_details[0][3]}
    {get_student_details[0][4]}
    {get_student_details[0][5]}
    """

        student_card_image_obj = draw_student_card(
            student_pic_path=student_pic,
            student_data=student_details
        )

        # Save Student Card
        def save_student_card():
                path = askdirectory()
        
                if path:        
                    student_card_image_obj.save(f'{path}/student_card.png')
        
            # Print Student Card
        def print_student_card():
            path = askdirectory()
                
            if path:                
                student_card_image_obj.save(f'{path}/student_card.png')
        
                win32api.ShellExecute(0, 'print', f'{path}/student_card.png',
                                          None, '.',0)
                    

        student_card_page_fm = tk.Frame(page_fm)
        student_card_page_fm.pack(fill=tk.BOTH, expand=True)

        student_card_img = ImageTk.PhotoImage(student_card_image_obj)

        student_card_lb = tk.Label(
            student_card_page_fm,
            image=student_card_img
        )
        student_card_lb.image = student_card_img
        student_card_lb.place(x=30, y=30)

        save_student_card_btn = tk.Button(
            student_card_page_fm,
            text='Save Student Card',
            font=('Bold', 15),
            bd=1,
            fg='white',
            bg=bg_color,
            command=save_student_card
        )
        save_student_card_btn.place(x=40, y=400)

        print_student_card_btn = tk.Button(
            student_card_page_fm,
            text='🖨️',
            font=('Bold', 15),
            bd=1,
            fg='white',
            bg=bg_color,
            command=print_student_card
        )
        print_student_card_btn.place(x=240, y=400)
        
    # create a Security Page inside dashboard frame
    def security_page():

        # For the locked Icon 
        def show_hide_password():
            if current_password_ent['show'] =='*':
                current_password_ent.config(show='')
                show_hide_btn.config(image=unlocked_icon)
            else:
                current_password_ent.config(show='*')
                show_hide_btn.config(image=locked_icon)


        # For change the password
        def set_password():

            # This condition change the password
            if new_password_ent.get() != '':
                confirm =confirmation_box(message='Do You Want to Change\nYour Password')
                if confirm:
                    connection = sqlite3.connect('students_accounts.db')
                    cursor = connection.cursor()
                    cursor.execute(f"""UPDATE data SET password = '{new_password_ent.get()}'
                                    WHERE id_number == '{student_id}'""")
                    connection.commit()
                    connection.close()
                    message_box(message='Password Change Successfully')

                    current_password_ent.config(state=tk.NORMAL)
                    current_password_ent.delete(0,tk.END)
                    current_password_ent.insert(0, new_password_ent.get())
                    current_password_ent.config(state='readonly')

                    new_password_ent.delete(0,tk.END)

            else:
                message_box(message="Enter New Password Required")



        # Frame
        security_page_fm = tk.Frame(page_fm,)

        # secyrity page label
        current_password_lb = tk.Label(security_page_fm,text='Your Current Password',
                                   font=('Bold',12))
        current_password_lb.place(x=80,y=30)

        # secyrity page entry
        current_password_ent = tk.Entry(security_page_fm,font=('Bold',15),
                                    justify=tk.CENTER,show='*')
        current_password_ent.place(x=50,y=80)

        # student Current Password from database
        student_current_password = fetch_student_data(f"SELECT password FROM data WHERE id_number == '{student_id}'")
        current_password_ent.insert(tk.END, student_current_password[0][0])
        current_password_ent.config(state='readonly')

        # Locked Icon
        show_hide_btn = tk.Button(security_page_fm,image=locked_icon,bd=0,
                                    command=show_hide_password)
        show_hide_btn.place(x=280,y=70)

        # Change Password 
        change_password_lb = tk.Label(security_page_fm,text='Change Password',
                                   font=('BOld',15),bg='red',fg='white',
                                   )
        change_password_lb.place(x=30,y=210,width=290)

        # add a New Password
        new_password_lb = tk.Label(security_page_fm,text='Set New Password',
                                   font=('Bold',12))
        new_password_lb.place(x=100,y=280)

        # new password Entry
        new_password_ent = tk.Entry(security_page_fm,font=('Bold',15),
                                    justify=tk.CENTER)
        new_password_ent.place(x=60,y=330)

        # change password button
        change_password_button = tk.Button(security_page_fm,text='SET Password',
                                           font=('Bold',15),bg=bg_color,fg='white',
                                           command =set_password)
        change_password_button.place(x=110,y=380)

        security_page_fm.pack(fill=tk.BOTH,expand=True)

        
    # For edit the exsisting data inside the dashboard card
    def edit_data_page():

        edit_data_page_fm = tk.Frame(page_fm,)
        edit_data_page_fm.pack(fill=tk.BOTH,expand=True)

        # Add Picture in Picture Frame
        pic_path = tk.StringVar()
        pic_path.set('')
    
        def open_pic():
            path = askopenfilename()
    
            if path:
                img = ImageTk.PhotoImage(Image.open(path).resize((100,100)))
                pic_path.set(path)
    
                add_pic_btn.config(image=img)
                add_pic_btn.image = img


        # Remove The High light Entry Color 
        def remove_highlight_warning(entry):
            if entry['highlightbackground'] != 'gray':
                if entry.get() != '':
                    entry.config(highlightcolor=bg_color,
                                highlightbackground='gray')

        # Check the Email Format
        def check_invalid_email(email):
            pattern = r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
            match = re.match(pattern=pattern,string=email)
            return match

        # Check the input that every box is not empty
        def check_input():

            nonlocal get_student_details, get_student_pic, student_pic

            # For name 
            if student_name_ent.get() == '':
                student_name_ent.config(highlightcolor='red',
                                        highlightbackground='red')
                student_name_ent.focus()
                message_box(message='Student Full Name Is Required')

            # For age
            elif student_age_ent.get() == '':
                student_age_ent.config(highlightcolor='red',
                                        highlightbackground='red')
                student_age_ent.focus()
                message_box(message='Student Age Is Required')

            # For Contact Number
            elif student_contact_ent.get() == '':
                student_contact_ent.config(highlightcolor='red',
                                        highlightbackground='red')
                student_contact_ent.focus()
                message_box(message='Student Contact Number Is Required')

            # For Email
            elif student_email_ent.get() == '':
                student_email_ent.config(highlightcolor='red',
                                        highlightbackground='red')
                student_email_ent.focus()
                message_box(message='Student Email Is Required')

            # For Valid Email
            elif not check_invalid_email(email=student_email_ent.get().lower()):
                student_email_ent.config(highlightcolor='red',
                                                        highlightbackground='red')
                student_email_ent.focus()
                message_box(message='Valid Email Is Required')

            # For image
            else:
                if pic_path.get() != '':
                    new_student_picture = Image.open(pic_path.get()).resize((100,100))
                    new_student_picture.save('temp_pic.png')

                    with open('temp_pic.png','rb') as read_new_pic:
                        new_picture_binary = read_new_pic.read()
                        read_new_pic.close()

                    connection = sqlite3.connect('students_accounts.db')
                    cursor = connection.cursor()

                    cursor.execute(f"""UPDATE data SET image=?
                    WHERE id_number == '{student_id}'
                    """,[new_picture_binary])

                    connection.commit()
                    connection.close()

                    message_box(message='Data Successfully Updated')

                # For all Detail update

                name = student_name_ent.get()
                age = student_age_ent.get()
                selected_class = student_class_btn.get()
                contact_number = student_contact_ent.get()
                email = student_email_ent.get()

                connection = sqlite3.connect('students_accounts.db')
                cursor = connection.cursor()

                cursor.execute(f"""
                UPDATE data SET name='{name}', age='{age}', class='{selected_class}',
                phone_number='{contact_number}', email='{email}'
                WHERE id_number == '{student_id}'
                """)

                connection.commit()
                connection.close()

                # For all Detail update on run time

                get_student_details = fetch_student_data(f"""
                    SELECT name, age, gender, class, phone_number, email 
                    FROM data 
                    where id_number =='{student_id}'
                    """)
                
                get_student_pic = fetch_student_data(f"""
                        SELECT image 
                        FROM data 
                        where id_number == '{student_id}'
                    """)
                
                student_pic = BytesIO(get_student_pic[0][0])

                message_box(message='Data Successfully Updated')


        student_current_pic = ImageTk.PhotoImage(Image.open(student_pic))

        # Add Picture Frame
        add_pic_section_fm=tk.Frame(edit_data_page_fm,highlightbackground=bg_color,
                                        highlightthickness=3)
        add_pic_section_fm.place(x=5,y=5,width=105,height=105)
    
        # Add Picture Button
        add_pic_btn=tk.Button(add_pic_section_fm,image=student_current_pic,bd=0,
                              command=open_pic)
        add_pic_btn.image = student_current_pic
        add_pic_btn.pack()

        # Name Entry
        student_name_lb = tk.Label(edit_data_page_fm,text="Student Full Name",font=('Bold',12),)
        student_name_lb.place(x=5,y=130)
        student_name_ent = tk.Entry(edit_data_page_fm,font=('Bold',15),
                                    highlightcolor=bg_color,highlightbackground='grey',
                                    highlightthickness=2)
        student_name_ent.place(x=5,y=160,width=180)
        student_name_ent.bind('<KeyRelease>',
                              lambda e:remove_highlight_warning(entry=student_name_ent))

        student_name_ent.insert(tk.END, get_student_details[0][0])

        # Age Entry
        student_age_lb=tk.Label(edit_data_page_fm,text='Student Age',font=('Bold',12))
        student_age_lb.place(x=5,y=210)
        student_age_ent = tk.Entry(edit_data_page_fm,font=('Bold',15),
                                    highlightcolor=bg_color,highlightbackground='grey',
                                    highlightthickness=2)
        student_age_ent.place(x=5,y=235,width=180)
        student_age_ent.bind('<KeyRelease>',
                                  lambda e:remove_highlight_warning(entry=student_age_ent))
        
        student_age_ent.insert(tk.END, get_student_details[0][1])
    
        # Contact Entry
        student_contact_lb=tk.Label(edit_data_page_fm,text='Contact Phone Number',font=('Bold',12))
        student_contact_lb.place(x=5,y=285)
        student_contact_ent = tk.Entry(edit_data_page_fm,font=('Bold',15),
                                    highlightcolor=bg_color,highlightbackground='grey',
                                    highlightthickness=2)
        student_contact_ent.place(x=5,y=310,width=180)
        student_contact_ent.bind('<KeyRelease>',
                                  lambda e:remove_highlight_warning(entry=student_contact_ent))

        student_contact_ent.insert(tk.END, get_student_details[0][4])
        
    
        # Choice Class Entry
        student_class_lb=tk.Label(edit_data_page_fm,text='Student Class',font=('Bold',12))
        student_class_lb.place(x=5,y=360)
        student_class_btn = Combobox(edit_data_page_fm,font=('Bold',15),
                                    state='readonly',values=Class_list,)
        student_class_btn.place(x=5,y=390,width=180,height=30)

        student_class_btn.set(get_student_details[0][3])
        

        # Email Id Entry
        student_email_lb=tk.Label(edit_data_page_fm,text='Student Email ID',font=('Bold',12))
        student_email_lb.place(x=5,y=440)
        student_email_ent = tk.Entry(edit_data_page_fm,font=('Bold',15),
                                    highlightcolor=bg_color,highlightbackground='grey',
                                    highlightthickness=2)
        student_email_ent.place(x=5,y=470,width=180)
        student_email_ent.bind('<KeyRelease>',
                                  lambda e:remove_highlight_warning(entry=student_email_ent))

        student_email_ent.insert(tk.END, get_student_details[0][5])


        # Upade Button for update the data 
        update_data_btn = tk.Button(edit_data_page_fm,text='Update',font=('Bold',15),
                                    fg='white', bg=bg_color,bd=0,command=check_input)
        update_data_btn.place(x=220, y=470, width=80)


    # For Delete Account 
    def delete_page():

        # For Delete the Account take the confirmation from user 
        def confirm_delete_account():
            confirm = confirmation_box(message="⚠️ Do You Want to Delete\nYour Account?")

            if confirm:
                connection = sqlite3.connect('students_accounts.db')
                cursor = connection.cursor()

                cursor.execute(f"""
                DELETE FROM data WHERE id_number == '{student_id}'
                """)

                connection.commit()
                connection.close()

                # Destroy the current page and going back to welcome page
                dashboard_fm.destroy()
                welcome_page()
                root.update()
                message_box(message='Account Successfully Delete')


        delete_account_page_fm = tk.Frame(page_fm)
        delete_account_page_fm.pack(fill=tk.BOTH,expand=True)

        # Label for delete account 
        delete_account_lb = tk.Label(delete_account_page_fm,text='⚠️ Delete Account',
                                     bg='red',fg='white',font=('Bold',15))
        delete_account_lb.place(x=30,y=100,width=290)

        # Delete Button
        delete_account_button = tk.Button(delete_account_page_fm,text='DELETE Account', bg='red',fg='white',
                                          font=('Bold',13),command=confirm_delete_account)
        delete_account_button.place(x=110,y=200)

    # create a frame inside a student card page 
    page_fm = tk.Frame(dashboard_fm)
    page_fm.place(x=122,y=5,width=350,height=550)

    home_page()
    

####### Student Login Page
def student_login_page():

    # For the locked Icon 
    def show_hide_password():
        if password_ent['show'] =='*':
            password_ent.config(show='')
            show_hide_btn.config(image=unlocked_icon)
        else:
            password_ent.config(show='*')
            show_hide_btn.config(image=locked_icon)

    # Forward to welcom page / Back to Welcome page
    def forward_to_welcome_page():
        student_login_page_fm.destroy()
        welcome_page()

    def forword_to_forget_password_page():
        forget_password_page()

    # Remove The High light Entry Color 
    def remove_highlight_warning(entry):
            if entry['highlightbackground'] != 'gray':
                if entry.get() != '':
                    entry.config(highlightcolor=bg_color,
                                highlightbackground='gray')

    # Login Functionality for the either the id is correct or incorrect               
    def login_account():
        verify_id_number = check_id_already_exists(id_number=id_number_ent.get())

        if verify_id_number:
            

            verify_password = check_valid_password(id_number=id_number_ent.get(),
                                                   password=password_ent.get())

            if verify_password:
                id_number=id_number_ent.get()
                student_login_page_fm.destroy()
                student_dashborad(student_id=id_number)
                root.update()

            else:
                print('!oops Password is Incorrect')
                password_ent.config(highlightcolor='red',
                                                highlightbackground='red')
                
                message_box(message='Incorrect Password')


        else:
            print('!OOPs ID is Incorrect')
            id_number_ent.config(highlightcolor='red',
                                highlightbackground='red')

            message_box(message='Please Enter Valid Student ID')


    # Student Login Frame
    student_login_page_fm = tk.Frame(root,highlightbackground=bg_color,highlightthickness=3)

    # Student Page Frame heading
    heading_lb=tk.Label(student_login_page_fm,text="Student Login Page",
                            bg=bg_color,fg='white',font=('Bold',18))
    heading_lb.place(x=0,y=0,width=400)

    # Back Button
    back_btn=tk.Button(student_login_page_fm,text='←',font=('Bold',20),bg=bg_color,
                       bd=0,command=forward_to_welcome_page)
    back_btn.place(x=5,y=40)

    # Student Icon
    stud_icon_lb= tk.Label(student_login_page_fm,image=login_student_icon)
    stud_icon_lb.place(x=150,y=40)

    # Student Details

    # Entry Box
    id_number_lb = tk.Label(student_login_page_fm,text="Enter Student Id Number",font=('Bold',15),fg=bg_color)
    id_number_lb.place(x=80,y=140)
    id_number_ent = tk.Entry(student_login_page_fm,font=('Bold',15),justify=tk.CENTER,
                            highlightcolor=bg_color,highlightbackground='grey',highlightthickness=2)
    id_number_ent.place(x=80,y=190)
    id_number_ent.bind('<KeyRelease>', 
                       lambda e:remove_highlight_warning(entry=id_number_ent))

    # Passward Box
    password_lb = tk.Label(student_login_page_fm,text="Enter Student Password",font=('Bold',15),fg=bg_color)
    password_lb.place(x=80,y=240)
    password_ent = tk.Entry(student_login_page_fm,font=('Bold',15),justify=tk.CENTER,
                            highlightcolor=bg_color,highlightbackground='grey',
                            highlightthickness=2,show='*')
    password_ent.place(x=80,y=290)
    password_ent.bind('<KeyRelease>', 
                       lambda e:remove_highlight_warning(entry=password_ent))


    # Locked Icon
    show_hide_btn = tk.Button(student_login_page_fm,image=locked_icon,bd=0,
                            command=show_hide_password)
    show_hide_btn.place(x=310,y=280)

    # Login Btn
    login_btn = tk.Button(student_login_page_fm,text='Login',font=('Bold',15),
                          bg=bg_color,fg='white',command=login_account)
    login_btn.place(x=95,y=340,width=200,height=40)

    # Forget Password Btn
    forget_password=tk.Button(student_login_page_fm,text='⚠️\nForget Password',
                            fg=bg_color,bd=0,
                            command=forword_to_forget_password_page)
    forget_password.place(x=150,y=390)

#////////////////////////////////////////////////////////////////////
    student_login_page_fm.pack_propagate(False)
    student_login_page_fm.pack(pady=30)
    student_login_page_fm.configure(width=400,height=450)


# Create a Admin Password
def admin_dashboard():

    # Switch colour of page Frame inside admin Dashboard
    def switch(indicator, page):
        home_btn_indicator.config(bg='#c3c3c3')
        find_student_btn_indicator.config(bg='#c3c3c3')
        announcement_btn_indicator.config(bg='#c3c3c3')

        indicator.config(bg=bg_color)

        for child in page_fm.winfo_children():
            child.destroy()
            root.update()

        page()


    # Home Page inside page Frame
    def home_page():

        # Frame
        home_page_fm = tk.Frame(page_fm)
        home_page_fm.pack(fill=tk.BOTH,expand=True)

        # admin image 
        admin_icon_lb = tk.Label(home_page_fm,image=login_admin_icon)
        admin_icon_lb.image = login_admin_icon
        admin_icon_lb.place(x=10, y=10)

        hi_lb = tk.Label(home_page_fm, text='!Hi Admin', font=('Bold',15))
        hi_lb.place(x=120,y=40)

        class_list_lb = tk.Label(home_page_fm, text='Number of Students By Class.',
                                 font=('Bold',13), bg=bg_color, fg='white')
        class_list_lb.place(x=20,y=130) 

        students_numbers_lb = tk.Label(home_page_fm, text='',font=('Bold',13),
                                       justify=tk.LEFT)
        students_numbers_lb.place(x=20,y=170)

        # Fetching the class data from database
        for i in Class_list:
            result = fetch_student_data(query=f"SELECT COUNT(*) FROM data WHERE class == '{i}'")
            students_numbers_lb['text'] += f"{i} Class: {result[0][0]}\n\n"
            # print(i,result)


    # Dashboard Frame
    dashboard_fm = tk.Frame(root,highlightbackground=bg_color,
                            highlightthickness=3)

    # Option Frame Button
    options_fm = tk.Frame(dashboard_fm,highlightbackground=bg_color,
                            highlightthickness=3,bg='#c3c3c3')

    # Home Button in Option Frame
    home_btn = tk.Button(options_fm,text='Home', font=('Bold',15),
                         fg=bg_color, bg='#c3c3c3',bd=0,
                         command=lambda:switch(indicator=home_btn_indicator,page=home_page))
    home_btn.place(x=10,y=50)

    home_btn_indicator = tk.Label(options_fm, text='', bg=bg_color)
    home_btn_indicator.place(x=5,y=48,width=3,height=40)

    # Create Find Button in option Frame
    find_student_btn = tk.Button(options_fm,text='Find\nStudent', font=('Bold',15),
                             fg=bg_color, bg='#c3c3c3',bd=0,justify=tk.LEFT,
                             command=lambda:switch(indicator=find_student_btn_indicator,
                                                   page=find_student_page))
    find_student_btn.place(x=10,y=100)
    
    find_student_btn_indicator = tk.Label(options_fm, text='', bg='#c3c3c3')
    find_student_btn_indicator.place(x=5,y=108,width=3,height=40)

    # Create Announcement Button in option Frame
    announcement_btn = tk.Button(options_fm,text='Announce\n-Ment🔊', font=('Bold',15),
                             fg=bg_color, bg='#c3c3c3',bd=0,command=lambda:switch(indicator=announcement_btn_indicator,
                                                                                  page=announcement_page))
    announcement_btn.place(x=10,y=170)
    
    announcement_btn_indicator = tk.Label(options_fm, text='', bg='#c3c3c3')
    announcement_btn_indicator.place(x=5,y=180,width=3,height=40)
    

    def logout():
        confirm = confirmation_box(message="Do You Want to\nLogout")

        if confirm:
            dashboard_fm.destroy()
            welcome_page()
            root.update()


    # Create Logout Button in option Frame
    logout_btn = tk.Button(options_fm, text='Logout', font=('Bold',15),
                           fg=bg_color,bg='#c3c3c3',bd=0,
                           command=logout)
    logout_btn.place(x=10,y=240)


#//////////////////////////////////////////////////////////   
    options_fm.place(x=0,y=0,width=120,height=575)

    # Create a find page inside pafe frame
    def find_student_page():

        def find_student():
            # Clear old records from table
            for item in record_table.get_children():
                record_table.delete(item)

            found_data = ''

            if find_by_option_btn.get() == 'id':
                found_data = fetch_student_data(query=f"""
                SELECT id_number, name, class, gender FROM data
                WHERE id_number == '{search_input.get()}'
                """)
                # print(found_data)

            elif find_by_option_btn.get() == 'name':
                found_data = fetch_student_data(query=f"""
                SELECT id_number, name, class, gender FROM data
                WHERE name Like '%{search_input.get()}%'
                """)
                # print(found_data)

            elif find_by_option_btn.get() == 'class':
                found_data = fetch_student_data(query=f"""
                SELECT id_number, name, class, gender FROM data
                WHERE class == '{search_input.get()}'
                """)
                # print(found_data)

            elif find_by_option_btn.get() == 'gender':
                found_data = fetch_student_data(query=f"""
                SELECT id_number, name, class, gender FROM data
                WHERE gender == '{search_input.get()}'
                """)
                # print(found_data)

            if found_data:

                for item in record_table.get_children():
                    record_table.delete(item)

                for details in found_data:
                    record_table.insert(parent='',index='end',values=details)

            else:
                for item in record_table.get_children():
                    record_table.delete(item)


        def generate_student_card():

            selection = record_table.selection()
            selected_id = record_table.item(item=selection, option='values')[0]
            get_student_details = fetch_student_data(f"""
                SELECT name, age, gender, class, phone_number, email 
                FROM data 
                where id_number =='{selected_id}'
                """)
            
            get_student_pic = fetch_student_data(f"""
                    SELECT image 
                    FROM data 
                    where id_number == '{selected_id}'
                """)
            
            student_pic = BytesIO(get_student_pic[0][0])

            student_details = f"""
{selected_id}
{get_student_details[0][0]}
{get_student_details[0][2]}
{get_student_details[0][1]}
{get_student_details[0][3]}
{get_student_details[0][4]}
{get_student_details[0][5]}            
      """
            
            student_card_image_obj = draw_student_card(
                        student_pic_path=student_pic,
                        student_data=student_details
            )

            student_card_page(student_card_obj=student_card_image_obj,
                              bypass_login_page=True)


        def clear_result():
            find_by_option_btn.set('id')

            search_input.delete(0,tk.END)

            for item in record_table.get_children():
                record_table.delete(item)

            generate_student_card_btn.config(state=tk.DISABLED)





 
        search_filters = ['id','name','class','gender']

        find_student_page_fm = tk.Frame(page_fm)


        find_student_page_lb = tk.Label(find_student_page_fm,text='Find Student Record',
                                        font=('Bold',13),fg='White',bg=bg_color)
        find_student_page_lb.place(x=20,y=10,width=300)


        find_by_lb = tk.Label(find_student_page_fm, text='Find By:', font=('Bold',12))
        find_by_lb.place(x=15,y=50)


        find_by_option_btn = Combobox(find_student_page_fm,font=('Bold',15),
                                      state='readonly',values=search_filters)
        find_by_option_btn.place(x=80, y=50, width=80)
        find_by_option_btn.set('id')


        search_input = tk.Entry(find_student_page_fm, font=('Bold',12))
        search_input.place(x=20, y=90)
        search_input.bind('<KeyRelease>',lambda e: find_student())


        record_table_lb = tk.Label(find_student_page_fm, text='Record Table',
                                   font=('Bold',13), bg=bg_color,fg='white')
        record_table_lb.place(x=20, y=160, width=300)


        record_table = Treeview(find_student_page_fm)
        record_table.place(x=0, y=200, width=350)
        record_table.bind('<<TreeviewSelect>>',lambda e:generate_student_card_btn.config(state=tk.NORMAL))

        record_table['columns'] = ('id','name','class','gender')

        record_table.column('#0', stretch=tk.NO, width=0)

        record_table.heading('id', text='ID Number', anchor=tk.W)
        record_table.column('id', width=50, anchor=tk.W)

        record_table.heading('name', text='Name', anchor=tk.W)
        record_table.column('name', width=90, anchor=tk.W)

        record_table.heading('class', text='Class', anchor=tk.W)
        record_table.column('class', width=40, anchor=tk.W)

        record_table.heading('gender', text='Gender', anchor=tk.W)
        record_table.column('gender', width=40, anchor=tk.W)


        generate_student_card_btn = tk.Button(find_student_page_fm,
                                              text='Generate Student Card',
                                              font=('Bold',13), bg=bg_color, fg='white',
                                              state=tk.DISABLED,command=generate_student_card)
        generate_student_card_btn.place(x=160, y=450)


        clear_btn = tk.Button(find_student_page_fm, text='Clear', font=('Bold',13),
                              bg=bg_color, fg='white',command=clear_result)
        clear_btn.place(x=10, y=450)



        



        find_student_page_fm.pack(fill=tk.BOTH, expand=True)


    # Create Announcement page inside admin dashboard
    def announcement_page():

        selected_classes = []

        def add_class(name):

            if selected_classes.count(name):
                selected_classes.remove(name)
            else:   
                selected_classes.append(name)
            print(selected_classes)

        def collect_emails():

            fetched_emails = []

            for _class in selected_classes:

                emails = fetch_student_data(f"SELECT email FROM data WHERE class == '{_class}'")

                for email_address in emails:
                    fetched_emails.append(*email_address)

            thread = threading.Thread(target=send_announcement, args=[fetched_emails])
            thread.start()


        def send_announcement(emails_addresses):

            box_fm = tk.Frame(root,highlightbackground=bg_color,
                              highlightthickness=3)

            heading_lb = tk.Label(box_fm, text='Sending Email', font=('Bold',15),
                                  bg=bg_color, fg='white')
            heading_lb.place(x=0, y=0, width=300)

            sending_lb = tk.Label(box_fm, font=('Bold',12), justify=tk.LEFT,
                                  text='Sending To\n:abc@gmail.com\n\n1/1')
            sending_lb.pack(pady=50)
            
            box_fm.place(x=100, y=120, width=300, height=200)

            subject = announcement_subject.get()
            message = f"<h3 style='white-space:pre-wrap;'>{announcement_message.get('0.1', tk.END)}</h3>"

            sent_count = 0
            for email in emails_addresses:

                sending_lb.config(text=f"Sending To:\n{email}\n\n{sent_count}/{len(emails_addresses)}")
                seadmail_to_student(email=email,
                                    subject = subject,
                                    message=message)
                sent_count += 1
                sending_lb.config(text=f"Sending To:\n{email}\n\n{sent_count}/{len(emails_addresses)}")

            box_fm.destroy()
            message_box(message="Announcement Sent\nSuccessfully")

        # Announcement Page Frame
        announcement_page_fm = tk.Frame(page_fm)

        # Label
        subject_lb = tk.Label(announcement_page_fm, text='Enter Announcement Subject.',
                              font=('Bold',12))
        subject_lb.place(x=10,y=10)

        # Subject Entry Box
        announcement_subject = tk.Entry(announcement_page_fm, font=('Bold',12))
        announcement_subject.place(x=10,y=40,width=210,height=25)

        # Create a message Box 
        announcement_message = ScrolledText(announcement_page_fm, font=('Bold',12))
        announcement_message.place(x=10,y=100,width=300,height=200)

        # Classes list
        classes_list_lb = tk.Label(announcement_page_fm, text='Select Classes to Announcement',
                                   font=('Bold',12))
        classes_list_lb.place(x=10,y=320)


        y_position = 350
        for grade in Class_list:
            class_check_btn = tk.Checkbutton(announcement_page_fm, text=f'Class {grade}',
                                             command=lambda grade=grade:add_class(name=grade))
            class_check_btn.place(x=10, y=y_position)
            y_position+=25

        # Send Announcement Button 
        send_announcement_btn = tk.Button(announcement_page_fm, text='Send Announcement',
                                          font=('Bold',12),bg=bg_color, fg='white',
                                          command=collect_emails)
        send_announcement_btn.place(x=180,y=520) 


#//////////////////////////////////////////////////////////////////////////////
        announcement_page_fm.pack(fill=tk.BOTH, expand=True)

    # Create Page Frame inside Admin Dashboard
    page_fm = tk.Frame(dashboard_fm, bg='gray')
    page_fm.place(x=122,y=5,width=350,height=550)

    # announcement_page()
    # find_student_page()
    home_page()


#////////////////////////////////////////////////////////////////////////
    dashboard_fm.pack(pady=5)
    dashboard_fm.pack_propagate(False)
    dashboard_fm.configure(width=480, height=580)


####### Admin Login Page
def admin_login_page(): 
    # For the locked Icon 
    def show_hide_password():
        if password_ent['show'] =='*':
            password_ent.config(show='')
            show_hide_btn.config(image=unlocked_icon)
        else:
            password_ent.config(show='*')
            show_hide_btn.config(image=locked_icon)

    
    # Forward to welcom page / Back to Welcome page
    def forward_to_welcome_page():
        admin_login_page_fm.destroy()
        welcome_page()

    def login_account():
        if username_ent.get() == 'admin':

            if password_ent.get() =='admin':
                admin_login_page_fm.destroy()
                root.update()
                admin_dashboard()

            else:
                message_box(message='Wrong Password')

        else:
            message_box(message='Wrong Username')


    # Addmin Frame
    admin_login_page_fm = tk.Frame(root,highlightbackground=bg_color,
                                highlightthickness=3)



    # Admin Frame heading
    heading_lb=tk.Label(admin_login_page_fm,text="Admin Login Page",
                                bg=bg_color,fg='white',font=('Bold',18))
    heading_lb.place(x=0,y=0,width=400)

    # Back Button
    back_btn=tk.Button(admin_login_page_fm,text='←',font=('Bold',20),bg=bg_color,
                           bd=0,command=forward_to_welcome_page)
    back_btn.place(x=5,y=40)



    # Admin Icon
    admin_icon_lb= tk.Label(admin_login_page_fm,image=login_admin_icon)
    admin_icon_lb.place(x=150,y=40)


    # Admin Details

    # Entry Box
    username_lb = tk.Label(admin_login_page_fm,text="Enter Admin User Name",font=('Bold',15),fg=bg_color)
    username_lb.place(x=80,y=140)
    username_ent = tk.Entry(admin_login_page_fm,font=('Bold',15),justify=tk.CENTER,
                                highlightcolor=bg_color,highlightbackground='grey',highlightthickness=2)
    username_ent.place(x=80,y=190)

    # Passward Box
    password_lb = tk.Label(admin_login_page_fm,text="Enter Admin Password",font=('Bold',15),fg=bg_color)
    password_lb.place(x=80,y=240)
    password_ent = tk.Entry(admin_login_page_fm,font=('Bold',15),justify=tk.CENTER,
                                highlightcolor=bg_color,highlightbackground='grey',
                                highlightthickness=2,show='*')
    password_ent.place(x=80,y=290)

    # Locked Icon
    show_hide_btn = tk.Button(admin_login_page_fm,image=locked_icon,bd=0,
                                command=show_hide_password)
    show_hide_btn.place(x=310,y=280)

    # Login Btn
    login_btn = tk.Button(admin_login_page_fm,text='Login',font=('Bold',15),bg=bg_color,
                          fg='white',command=login_account)
    login_btn.place(x=95,y=340,width=200,height=40)

#////////////////////////////////////////////////////////////////////
    admin_login_page_fm.pack(pady=30)
    admin_login_page_fm.pack_propagate(False)
    admin_login_page_fm.configure(width=400,height=430)
 


Student_gender = tk.StringVar()  # For Radio Button of Male And Female
Class_list = ['5th','6th','7th','8th','9th','10th','11th','12th']  # For Combobox Choices

####### Create Account Page
def add_account_page():

    # Add Picture in Picture Frame
    pic_path = tk.StringVar()
    pic_path.set('')

    def open_pic():
        path = askopenfilename()

        if path:
            img = ImageTk.PhotoImage(Image.open(path).resize((100,100)))
            pic_path.set(path)

            add_pic_btn.config(image=img)
            add_pic_btn.image = img

    # Forward to welcom page / Back to Welcome page
    def forward_to_welcome_page():

        ans = confirmation_box('Do You Wnat To Leave\nRegistration Foam')
        if ans:
            add_account_page_fm.destroy()
            root.update()
            welcome_page()

    # Remove The High light Entry Color 

    def remove_highlight_warning(entry):
        if entry['highlightbackground'] != 'gray':
            if entry.get() != '':
                entry.config(highlightcolor=bg_color,
                            highlightbackground='gray')

    # Generate Uniqe ID number For Every User
    def generate_id_number():
        generated_id = ''

        for r in range(6):
            generated_id += str(random.randint(0,9))

        if not check_id_already_exists(id_number=generated_id):  
            print('id number:',generated_id)

            student_id_ent.config(state=tk.NORMAL)
            student_id_ent.delete(0,tk.END)
            student_id_ent.insert(tk.END, generated_id)
            student_id_ent.config(state='readonly')

        else:
            generate_id_number()

    # Check the Email Format
    def check_invalid_email(email):
        pattern = r"^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$"
        match = re.match(pattern=pattern,string=email)
        return match


    # Check Input Validation 
    def check_input_validation():
        if student_name_ent.get() == '':
            student_name_ent.config(highlightcolor='red',
                                     highlightbackground='red')
            student_name_ent.focus()
            message_box('Student Full Name is Required')

        elif student_age_ent.get() == '':
            student_age_ent.config(highlightcolor='red',
                                 highlightbackground='red')
            student_age_ent.focus()
            message_box('Student Age is Required')

        elif student_contact_ent.get() == '':
            student_contact_ent.config(highlightcolor='red',
                                         highlightbackground='red')
            student_contact_ent.focus()
            message_box('Student Contact Number is Required')

        elif student_id_ent.get() == '':
            student_id_ent.config(highlightcolor='red',
                                         highlightbackground='red')
            student_id_ent.focus()
            message_box('Student ID is Required')

        elif student_class_btn.get() == '':
                    student_class_btn.focus()
                    message_box('Fill The Class')

        elif student_email_ent.get() == '':
            student_email_ent.config(highlightcolor='red',
                                         highlightbackground='red')
            student_email_ent.focus()
            message_box('Student Email is Required')

        elif not check_invalid_email(email=student_email_ent.get().lower()):
            student_email_ent.config(highlightcolor='red',
                                    highlightbackground='red')
            student_email_ent.focus()
            message_box("Please Enter a Valid Email Address")

        elif account_password_ent.get() == '':
            account_password_ent.config(highlightcolor='red',
                                 highlightbackground='red')
            account_password_ent.focus()
            message_box('Create Password')

        else:

            # pic_path = b''

            if  pic_path.get() != '':
                resize_pic = Image.open(pic_path.get()).resize((100,100))
                resize_pic.save('temp_pic.png')

                read_data = open('temp_pic.png','rb')
                pic_data = read_data.read()
                read_data.close()

            else:

                read_data = open(r'Images\add_image.png','rb')
                pic_data = read_data.read()
                read_data.close()
                pic_path.set(r'Images\add_image.png')

            add_data(
                     id_number=student_id_ent.get(),
                     password=account_password_ent.get(),
                     name=student_name_ent.get(),
                     age=student_age_ent.get(),
                     gender=Student_gender.get(),
                     phone_number=student_contact_ent.get(),
                     student_class=student_class_btn.get(),
                     email=student_email_ent.get(),
                     pic_data=pic_data
                    )
            


# Getting Student Data For Student Card
            data = f"""
{student_id_ent.get()}
{student_name_ent.get()}
{Student_gender.get()}
{student_age_ent.get()}
{student_class_btn.get()}
{student_contact_ent.get()}
{student_email_ent.get()}
"""

            # Taking Student Data For Student Card
            get_student_card = draw_student_card(student_pic_path=pic_path.get(),
                              student_data=data)

            student_card_page(student_card_obj=get_student_card)

            add_account_page_fm.destroy()
            root.update()

            message_box('Account Successful Created')

    ######### Create Account Frame
    add_account_page_fm = tk.Frame(root,highlightbackground=bg_color,
                                    highlightthickness=3)

    # Add Picture Frame
    add_pic_section_fm=tk.Frame(add_account_page_fm,highlightbackground=bg_color,
                                    highlightthickness=3)
    add_pic_section_fm.place(x=5,y=5,width=105,height=105)

    # Add Picture Button
    add_pic_btn=tk.Button(add_pic_section_fm,image=add_student_pic_icon,bd=0,
                          command=open_pic)
    add_pic_btn.pack()

    # Add detail Section

    # Name Entry
    student_name_lb = tk.Label(add_account_page_fm,text="Enter Student Full Name",font=('Bold',12),)
    student_name_lb.place(x=5,y=130)
    student_name_ent = tk.Entry(add_account_page_fm,font=('Bold',15),
                                highlightcolor=bg_color,highlightbackground='grey',
                                highlightthickness=2)
    student_name_ent.place(x=5,y=160,width=180)
    student_name_ent.bind('<KeyRelease>',
                          lambda e:remove_highlight_warning(entry=student_name_ent))

    # Gender Entry
    student_gender_lb = tk.Label(add_account_page_fm,text="Select Student Gender",font=('Bold',12),)
    student_gender_lb.place(x=5,y=210)

    # Gender Button
    male_gender_btn = tk.Radiobutton(add_account_page_fm,text='Male',font=('Bold',12),
                                    variable=Student_gender,value='Male')
    male_gender_btn.place(x=5,y=235)

    female_gender_btn = tk.Radiobutton(add_account_page_fm,text='Female',font=('Bold',12),
                                    variable=Student_gender,value='Female')
    female_gender_btn.place(x=80,y=235)

    Student_gender.set('male')


    # Age Entry
    student_age_lb=tk.Label(add_account_page_fm,text='Enter Student Age',font=('Bold',12))
    student_age_lb.place(x=5,y=275)
    student_age_ent = tk.Entry(add_account_page_fm,font=('Bold',15),
                                highlightcolor=bg_color,highlightbackground='grey',
                                highlightthickness=2)
    student_age_ent.place(x=5,y=305,width=180)
    student_age_ent.bind('<KeyRelease>',
                              lambda e:remove_highlight_warning(entry=student_age_ent))
    

    # Contact Entry
    student_contact_lb=tk.Label(add_account_page_fm,text='Enter Contact Phone Number',font=('Bold',12))
    student_contact_lb.place(x=5,y=360)
    student_contact_ent = tk.Entry(add_account_page_fm,font=('Bold',15),
                                highlightcolor=bg_color,highlightbackground='grey',
                                highlightthickness=2)
    student_contact_ent.place(x=5,y=390,width=180)
    student_contact_ent.bind('<KeyRelease>',
                              lambda e:remove_highlight_warning(entry=student_contact_ent))
    

    # Choice Class Entry
    student_class_lb=tk.Label(add_account_page_fm,text='Select Student Class',font=('Bold',12))
    student_class_lb.place(x=5,y=445)
    student_class_btn = Combobox(add_account_page_fm,font=('Bold',15),
                                state='readonly',values=Class_list,)
    student_class_btn.place(x=5,y=475,width=180,height=30)
    
    


    # Student ID Entry
    student_id_lb=tk.Label(add_account_page_fm,text='Student ID Number:',font=('Bold',12))
    student_id_lb.place(x=240,y=36)
    student_id_ent = tk.Entry(add_account_page_fm,font=('Bold',18),bd=0)
    student_id_ent.place(x=380,y=36,width=80)
    student_id_ent.bind('<KeyRelease>',
                              lambda e:remove_highlight_warning(entry=student_id_ent))
    
    student_id_ent.config(state='readonly')

    generate_id_number()

    # Information about ID 
    id_info_id = tk.Label(add_account_page_fm,text="""Automaticaly Generated ID Number
! Remember Using This ID Number
Student will Login Account.""",justify=tk.LEFT)
    id_info_id.place(x=240,y=65)

    # Email Id Entry
    student_email_lb=tk.Label(add_account_page_fm,text='Enter Student Email ID',font=('Bold',12))
    student_email_lb.place(x=240,y=130)
    student_email_ent = tk.Entry(add_account_page_fm,font=('Bold',15),
                                highlightcolor=bg_color,highlightbackground='grey',
                                highlightthickness=2)
    student_email_ent.place(x=240,y=160,width=180)
    student_email_ent.bind('<KeyRelease>',
                              lambda e:remove_highlight_warning(entry=student_email_ent))
    

    # Email Information
    email_info_lb = tk.Label(add_account_page_fm,text="""Via Email Address Student
Can Recover Account
! In Case Forgetting Password and also
Student will get Future Notifications.""",justify=tk.LEFT)
    email_info_lb.place(x=240,y=200)

    # Account Password Entry
    account_password_lb=tk.Label(add_account_page_fm,text='Create Account Password',font=('Bold',12))
    account_password_lb.place(x=240,y=275)
    account_password_ent = tk.Entry(add_account_page_fm,font=('Bold',15),
                                highlightcolor=bg_color,highlightbackground='grey',
                                highlightthickness=2)
    account_password_ent.place(x=240,y=310,width=180)
    account_password_ent.bind('<KeyRelease>',
                              lambda e:remove_highlight_warning(entry=account_password_ent))
    

    # Password Informations
    create_password_info_lb = tk.Label(add_account_page_fm,text="""Via Studdent Created Password
And Provided Student ID Number
Student Can Login Account.""",justify=tk.LEFT)
    create_password_info_lb.place(x=240,y=350)

    # Home Button 
    home_button = tk.Button(add_account_page_fm,text='Home',font=('Bold',15),
                            bg='red',fg='white',bd=0,
                            command=forward_to_welcome_page)
    home_button.place(x=240,y=420)

    # Submit Button
    submit_button = tk.Button(add_account_page_fm,text='Submit',font=('Bold',15),
                            bg=bg_color,fg='white',bd=0,
                            command=check_input_validation)
    submit_button.place(x=360,y=420)

    #//////////////////////////////////////////////////////////////////////
    add_account_page_fm.pack(pady=5)
    add_account_page_fm.pack_propagate(False)
    add_account_page_fm.configure(width=480,height=580)



init_database()
welcome_page()
# add_account_page()
# draw_student_card()
# student_login_page()
# forget_password_page()
# student_dashborad(student_id=472680)
# admin_dashboard()
# admin_login_page()
root.mainloop()

