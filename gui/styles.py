# gui/styles.py

LIGHT = """
    QMainWindow, QWidget {
        background-color: #f5f4f0;
        color: #1a1a1a;
        font-size: 13px;
    }
    QLineEdit {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 10px 14px;
        color: #1a1a1a;
        font-size: 13px;
    }
    QLineEdit:focus {
        border: 1px solid #aaa;
    }
    QPushButton#add_btn {
        background-color: #18181b;
        color: #ffffff;
        border: none;
        border-radius: 10px;
        font-size: 28px;
        font-weight: 200;
        padding: 4px;
        margin: 0;
    }
    QPushButton#add_btn:hover {
        background-color: #333;
    }
    QPushButton#theme_btn {
        background-color: #ffffff;
        color: #1a1a1a;
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 8px 16px;
    }
    QPushButton#theme_btn:hover {
        background-color: #efefef;
    }
    QPushButton#title_btn {
        background-color: transparent;
        color: #1a1a1a;
        border: none;
        font-size: 18px;
        font-weight: bold;
        padding: 0;
    }
    QTableWidget {
        background-color: #ffffff;
        border: 1px solid #e8e8e8;
        border-radius: 12px;
        gridline-color: #f0f0f0;
        font-size: 13px;
    }
    QHeaderView::section {
        background-color: #ffffff;
        color: #999;
        font-size: 11px;
        font-weight: normal;
        border: none;
        border-bottom: 1px solid #f0f0f0;
        padding: 10px 12px;
    }
    QTableWidget::item {
        padding: 10px 12px;
        border: none;
        color: #1a1a1a;
    }
    QPushButton#delete_btn {
        background-color: transparent;
        color: #e24b4a;
        border: 1px solid #f0d0d0;
        border-radius: 8px;
        padding: 4px 12px;
        font-size: 12px;
    }
    QPushButton#delete_btn:hover {
        background-color: #fff0f0;
    }
"""

DARK = """
    QMainWindow, QWidget {
        background-color: #18181b;
        color: #f5f5f5;
        font-size: 13px;
    }
    QLineEdit {
        background-color: #27272a;
        border: 1px solid #3f3f46;
        border-radius: 10px;
        padding: 10px 14px;
        color: #f0f0f0;
        font-size: 13px;
    }
    QLineEdit:focus {
        border: 1px solid #666;
    }
    QPushButton#add_btn {
        background-color: #ffffff;
        color: #18181b;
        border: none;
        border-radius: 10px;
        font-size: 28px;
        font-weight: 200;
        padding: 4px;
        margin: 0;
    }
    QPushButton#add_btn:hover {
        background-color: #ddd;
    }
    QPushButton#theme_btn {
        background-color: #27272a;
        color: #f5f5f5;
        border: 1px solid #3f3f46;
        border-radius: 10px;
        padding: 8px 16px;
    }
    QPushButton#theme_btn:hover {
        background-color: #333;
    }
    QPushButton#title_btn {
        background-color: transparent;
        color: #f5f5f5;
        border: none;
        font-size: 18px;
        font-weight: bold;
        padding: 0;
    }
    QTableWidget {
        background-color: #27272a;
        border: 1px solid #3f3f46;
        border-radius: 12px;
        gridline-color: #333;
        font-size: 13px;
    }
    QHeaderView::section {
        background-color: #27272a;
        color: #666;
        font-size: 11px;
        font-weight: normal;
        border: none;
        border-bottom: 1px solid #333;
        padding: 10px 12px;
    }
    QTableWidget::item {
        padding: 10px 12px;
        border: none;
        color: #f0f0f0;
    }
    QPushButton#delete_btn {
        background-color: transparent;
        color: #e24b4a;
        border: 1px solid #4a2828;
        border-radius: 8px;
        padding: 4px 12px;
        font-size: 124px;
        padding: 4px 8px; 
    }
    QPushButton#delete_btn:hover {
        background-color: #2a1818;
    }
"""