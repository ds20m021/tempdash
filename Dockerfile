FROM python:3.8
COPY . /app
WORKDIR /app
RUN pip install -r requiremts.txt
ENTRYPOINT ["streamlit", "run"]
CMD ["board.py"]
EXPOSE 8501