FROM node:latest

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8085
CMD ["node", "app.js"]