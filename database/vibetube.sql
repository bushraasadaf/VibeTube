
-- 1. Genres Table 
CREATE TABLE Genres (
    genre_id   INT PRIMARY KEY IDENTITY(1,1), -- auto-incrementing Primary Key
    genre_name NVARCHAR(50) NOT NULL UNIQUE    -- Study, Travel, Entertainment etc
);

-- 2. Creators Table (User Type A)
CREATE TABLE Creators (
    creator_id  INT PRIMARY KEY IDENTITY(1,1),
    name        NVARCHAR(100) NOT NULL,
    email       NVARCHAR(255) NOT NULL UNIQUE,
    password    NVARCHAR(255) NOT NULL         -- Should store HASHED password
);


-- 3. Viewers Table (User Type B
CREATE TABLE Viewers (
    viewer_id   INT PRIMARY KEY IDENTITY(1,1),
    name        NVARCHAR(100) NOT NULL,
    email       NVARCHAR(255) NOT NULL UNIQUE,
    password    NVARCHAR(255) NOT NULL         -- store HASHED password
);


-- 4. Channels Table (Links Creator to their Channel)
CREATE TABLE Channels (
    channel_id   INT PRIMARY KEY IDENTITY(1,1),
    creator_id   INT NOT NULL UNIQUE, -- One channel per creator
    channel_name NVARCHAR(100) NOT NULL,
    
    -- Foreign Key Constraint
    CONSTRAINT FK_Channels_Creator
        FOREIGN KEY (creator_id)
        REFERENCES Creators(creator_id)
        ON DELETE CASCADE -- If a Creator is deleted, their Channel is deleted
);

---

-- 5. Videos Table 
CREATE TABLE Videos (
    video_id       INT PRIMARY KEY IDENTITY(1,1),
    channel_id     INT NOT NULL,
    genre_id       INT NOT NULL,
    title          NVARCHAR(255) NOT NULL,
    description    NVARCHAR(MAX),
    upload_date    DATE NOT NULL,
    views          INT NOT NULL DEFAULT 0,
    likes_count    INT NOT NULL DEFAULT 0,    
    comments_count INT NOT NULL DEFAULT 0,    
    
    -- Foreign Key Constraints
    CONSTRAINT FK_Videos_Channel
        FOREIGN KEY (channel_id)
        REFERENCES Channels(channel_id)
        ON DELETE CASCADE, -- If a channel is deleted, its videos are deleted
    
    CONSTRAINT FK_Videos_Genre
        FOREIGN KEY (genre_id)
        REFERENCES Genres(genre_id)
);


-- 6. Likes Table (Viewer Interaction)
CREATE TABLE Likes (
    viewer_id INT NOT NULL,
    video_id  INT NOT NULL,

    -- Defines the composite primary key, which also enforces uniqueness
    PRIMARY KEY (viewer_id, video_id),

    -- Foreign Key Constraints
    CONSTRAINT FK_Likes_Viewer_New
        FOREIGN KEY (viewer_id)
        REFERENCES Viewers(viewer_id)
        ON DELETE CASCADE,

    CONSTRAINT FK_Likes_Video_New
        FOREIGN KEY (video_id)
        REFERENCES Videos(video_id)
        ON DELETE CASCADE -- If video is deleted, remove all related likes
);

---

-- 7. Comments Table (Viewer Interaction)
CREATE TABLE Comments (
    comment_id   INT PRIMARY KEY IDENTITY(1,1),
    viewer_id    INT NOT NULL,
    video_id     INT NOT NULL,
    comment_text NVARCHAR(MAX) NOT NULL,
    comment_date DATETIME NOT NULL DEFAULT GETDATE(),
    
    -- Foreign Key Constraints
    CONSTRAINT FK_Comments_Viewer
        FOREIGN KEY (viewer_id)
        REFERENCES Viewers(viewer_id)
        ON DELETE NO ACTION, --keep viewer if they commented on smthn (unless the comment is deleted first)
        
    CONSTRAINT FK_Comments_Video
        FOREIGN KEY (video_id)
        REFERENCES Videos(video_id)
        ON DELETE CASCADE --if video is deleted remove all comments relatng to it
);


-- 8. Subscriptions Table (Viewer Interaction)
CREATE TABLE Subscriptions (
    viewer_id  INT NOT NULL,
    channel_id INT NOT NULL,

    -- Composite primary key enforces uniqueness
    PRIMARY KEY (viewer_id, channel_id),

    -- Foreign Key Constraints
    CONSTRAINT FK_Subscriptions_Viewer_New
        FOREIGN KEY (viewer_id)
        REFERENCES Viewers(viewer_id)
        ON DELETE CASCADE,

    CONSTRAINT FK_Subscriptions_Channel_New
        FOREIGN KEY (channel_id)
        REFERENCES Channels(channel_id)
        ON DELETE CASCADE
);



