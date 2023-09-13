Database for messenger
Ласевич Евгений 
153501

1.User authentication with secure password storage and recovery.
2.User management capabilities including creating, reading, updating, and deleting users.
3.A role system with standard and custom roles.
4.Role assignment and access rights management.
5.Access restrictions based on assigned roles.

      User: One-to many(Message), Many-to-One(Rles)
        User ID: INT (Primary Key, Auto Increment)
        First Name: VARCHAR(50) (limit to 50 characters)
        Last Name: VARCHAR(50) (limit to 50 characters)
        Email: VARCHAR(100) (limit to 100 characters, UNIQUE constraint)
        Password Hash: VARCHAR(255) (password hash, e.g., bcrypt)
        Registration Date: TIMESTAMP
        Other Personal Data: TEXT (for storing additional data)

    Roles: Many-to-One(User)
        Role ID: INT (Primary Key, Auto Increment)
        Role Name: VARCHAR(50) (limit to 50 characters)

    Chat: One-to-Many(Message), One-to-Many(User)
        Chat ID: INT (Primary Key, Auto Increment)
        Chat Name: VARCHAR(100) (limit to 100 characters)
        Creation Date: TIMESTAMP
        Chat Type: ENUM('Group', 'Private') (limit to possible values)

    Message: Many-to-One(User), Many-to-One(Chat), One-to-Many(Attachments), One-to-Many(ReadStatus)
        Message ID: INT (Primary Key, Auto Increment)
        Message Text: TEXT
        Send Date and Time: TIMESTAMP
        Sender ID: INT (reference to user)
        Chat ID: INT (reference to chat)

    Attachments: Many-to-One(Message)
        File ID: INT (Primary Key, Auto Increment)
        File Name: VARCHAR(255)
        File Type: VARCHAR(50)
        Message ID: INT (reference to message)

    ReadStatus: Many-to-One(Message), Many-to-One(User)
        Read Status ID: INT (Primary Key, Auto Increment)
        Message ID: INT (reference to message)
        User ID: INT (reference to user)
        Read Date and Time: TIMESTAMP

    ChatParticipants: Many-to-One(Chat), Many-to-One(User)
        Record ID: INT (Primary Key, Auto Increment)
        Chat ID: INT (reference to chat)
        User ID: INT (reference to user)
        Participant Role: ENUM('Administrator', 'Regular Participant')

    Notifications: Many-to-One(User), Many-to-One(Chat)
        Notification ID: INT (Primary Key, Auto Increment)
        Notification Type: ENUM('New Message', 'New Participant')
        User ID: INT (reference to user)
        Chat ID: INT (reference to chat)
        Notification Status: BOOLEAN (Read/Unread)

    BlockedUsers:Many-to_Many(User)
        Record ID: INT (Primary Key, Auto Increment)
        Blocking User ID: INT (reference to user)
        Blocked User ID: INT (reference to user)

    ChatSettings:One-to-Many(Chat)
        Record ID: INT (Primary Key, Auto Increment)
        Chat ID: INT (reference to chat)
        Chat Settings: JSON (or other type for storing settings)
