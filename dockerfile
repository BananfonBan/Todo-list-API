FROM python:3.10

WORKDIR /app

COPY . .

# Install dependencies
RUN make install

CMD ["make", "run"]
