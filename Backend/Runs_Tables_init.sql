-- Create LCCDE Runs Table
CREATE TABLE LCCDE (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    duration TIME,
    run_date DATE,
    accuracy DECIMAL(7,6),
    prec DECIMAL(7,6),
    recall DECIMAL(7,6),
    f1_score DECIMAL(7,6)
);

-- Create TreeBased table
CREATE TABLE TreeBased (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    duration TIME,
    run_date DATE,
    accuracy DECIMAL(7,6),
    prec DECIMAL(7,6),
    recall DECIMAL(7,6),
    f1_score DECIMAL(7,6)
);

-- Create MTH table
CREATE TABLE MTH (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    duration TIME,
    run_date DATE,
    accuracy DECIMAL(7,6),
    prec DECIMAL(7,6),
    recall DECIMAL(7,6),
    f1_score DECIMAL(7,6)
);

-- Combined tables into one main table (CombinedRuns)
CREATE TABLE RunHistory (
    run_id INT AUTO_INCREMENT PRIMARY KEY,
    duration TIME,
    run_date DATE
);

-- holds unique ids
CREATE TABLE unique_ids (
    id INT AUTO_INCREMENT PRIMARY KEY
);

DELIMITER $$

-- insert into combined table trigger
CREATE TRIGGER insert_history_lccde 
AFTER INSERT 
ON ids_db.lccde FOR EACH ROW
BEGIN
	INSERT INTO runhistory (run_id, duration, run_date)
    VALUES (new.run_id, new.duration, new.run_date);
END $$

CREATE TRIGGER insert_history_treebased
AFTER INSERT 
ON ids_db.treebased FOR EACH ROW
BEGIN
	INSERT INTO runhistory (run_id, duration, run_date)
    VALUES (new.run_id, new.duration, new.run_date);
END $$

CREATE TRIGGER insert_history_mth
AFTER INSERT 
ON ids_db.mth FOR EACH ROW
BEGIN
	INSERT INTO runhistory (run_id, duration, run_date)
    VALUES (new.run_id, new.duration, new.run_date);
END $$

-- unique id assignment
CREATE TRIGGER lccde_insert_trigger
BEFORE INSERT ON lccde
FOR EACH ROW
BEGIN
    INSERT INTO unique_ids() VALUES ();
    SET NEW.run_id = LAST_INSERT_ID();
END$$

CREATE TRIGGER treebased_insert_trigger
BEFORE INSERT ON treebased
FOR EACH ROW
BEGIN
    INSERT INTO unique_ids() VALUES ();
    SET NEW.run_id = LAST_INSERT_ID();
END$$

CREATE TRIGGER mth_insert_trigger
BEFORE INSERT ON mth
FOR EACH ROW
BEGIN
    INSERT INTO unique_ids() VALUES ();
    SET NEW.run_id = LAST_INSERT_ID();
END$$
DELIMITER ;