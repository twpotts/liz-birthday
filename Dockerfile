FROM python:3.9.13
COPY requirements.txt /
RUN pip install -r requirements.txt
CMD sh setup.sh && streamlit run app.py