FROM node:20-slim AS build
WORKDIR /app
COPY package.json ./
RUN npm install
COPY . .
ENV NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
RUN npm run build

FROM node:20-slim
WORKDIR /app
COPY --from=build /app ./
EXPOSE 3000
CMD ["npm", "run", "start"]
