---------------------1------------------
CREATE TABLE MyTable (
    id NUMBER,
    val NUMBER
)


---------------------2------------------
DECLARE
    v_id NUMBER;
    v_val NUMBER;
BEGIN
    FOR i IN 1..10000 LOOP
        v_id := i;
        v_val := ROUND(DBMS_RANDOM.VALUE(1, 10000)); -- Генерация случайного числа от 1 до 10000
        INSERT INTO MyTable (id, val) VALUES (v_id, v_val);
    END LOOP;
    COMMIT; 
END;


---------------------3------------------
CREATE OR REPLACE FUNCTION check_even_odd RETURN VARCHAR2 IS
    v_even_count NUMBER := 0;
    v_odd_count NUMBER := 0;
BEGIN
    -- Подсчет количества четных и нечетных значений
    SELECT COUNT(CASE WHEN MOD(val, 2) = 0 THEN 1 END),
           COUNT(CASE WHEN MOD(val, 2) != 0 THEN 1 END)
    INTO v_even_count, v_odd_count
    FROM MyTable;

    -- Возвращение соответствующего результата
    IF v_even_count > v_odd_count THEN
        RETURN 'TRUE';
    ELSIF v_even_count < v_odd_count THEN
        RETURN 'FALSE';
    ELSE
        RETURN 'EQUAL';
    END IF;
END;


DECLARE
    result VARCHAR2(10);
BEGIN
    result := check_even_odd();
    DBMS_OUTPUT.PUT_LINE('Результат: ' || result);
END;

SELECT check_even_odd() FROM dual;


---------------------4------------------
CREATE OR REPLACE FUNCTION generate_insert_statement(p_id IN NUMBER, p_val IN NUMBER) RETURN VARCHAR2 IS
    v_insert_statement VARCHAR2(4000);
BEGIN
    v_insert_statement := 'INSERT INTO MyTable (id, val) VALUES (' || p_id || ', ' || p_val || ');';
    RETURN v_insert_statement;
END;

CREATE GLOBAL TEMPORARY TABLE temp_result (
    result VARCHAR2(4000)
) ON COMMIT PRESERVE ROWS;

DECLARE
    v_insert_command VARCHAR2(4000);
BEGIN
    v_insert_command := generate_insert_statement(123, 456); 
    INSERT INTO temp_result (result) VALUES (v_insert_command);
END;

SELECT result FROM temp_result;


----------------------5-----------------
CREATE OR REPLACE PROCEDURE insert_into_mytable(p_id IN NUMBER, p_val IN NUMBER) AS
BEGIN
    INSERT INTO MyTable (id, val) VALUES (p_id, p_val);
    COMMIT; -- Фиксация изменений
END insert_into_mytable;

CREATE OR REPLACE PROCEDURE update_mytable(p_id IN NUMBER, p_new_val IN NUMBER) AS
BEGIN
    UPDATE MyTable SET val = p_new_val WHERE id = p_id;
    COMMIT; -- Фиксация изменений
END update_mytable;

CREATE OR REPLACE PROCEDURE delete_from_mytable(p_id IN NUMBER) AS
BEGIN
    DELETE FROM MyTable WHERE id = p_id;
    COMMIT; -- Фиксация изменений
END delete_from_mytable;


BEGIN
    insert_into_mytable(1, 100); -- Вставка данных
    update_mytable(1, 200); -- Обновление данных
    delete_from_mytable(1); -- Удаление данных
END;


----------------------6-----------------
CREATE OR REPLACE FUNCTION calculate_annual_compensation(p_monthly_salary IN NUMBER, p_annual_bonus_percent IN NUMBER) RETURN NUMBER IS
    v_annual_bonus_percent NUMBER;
    v_annual_compensation NUMBER;
BEGIN
    -- Проверка на корректность ввода
    IF p_monthly_salary <= 0 OR p_annual_bonus_percent < 0 THEN
        RAISE_APPLICATION_ERROR(-20001, 'Некорректные данные: месячная зарплата должна быть положительным числом, а процент премии неотрицательным числом.');
    END IF;
    
    -- Преобразование процента к дробному числу
    v_annual_bonus_percent := p_annual_bonus_percent / 100;

    -- Вычисление общего вознаграждения за год
    v_annual_compensation := (1 + v_annual_bonus_percent) * 12 * p_monthly_salary;

    RETURN v_annual_compensation;
EXCEPTION
    WHEN OTHERS THEN
        RETURN NULL; -- Возвращаем NULL в случае ошибки
END calculate_annual_compensation;

SET SERVEROUTPUT ON;


DECLARE
    v_monthly_salary NUMBER := 5000; 
    v_annual_bonus_percent NUMBER := 10;
    v_annual_compensation NUMBER;
BEGIN
    v_annual_compensation := calculate_annual_compensation(v_monthly_salary, v_annual_bonus_percent);
    DBMS_OUTPUT.PUT_LINE('Общее вознаграждение за год: ' || v_annual_compensation);
END;
/



