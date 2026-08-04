import { INestApplication, ValidationPipe } from '@nestjs/common';
import { Test, TestingModule } from '@nestjs/testing';
import request from 'supertest';
import { AppModule } from '../app.module';

describe('CfpController', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    app.setGlobalPrefix('api');
    app.useGlobalPipes(
      new ValidationPipe({
        whitelist: true,
        forbidNonWhitelisted: true,
        transform: true,
      }),
    );
    await app.init();
  });

  afterAll(async () => {
    await app.close();
  });

  it('should reject invalid payload with 400 Bad Request', async () => {
    await request(app.getHttpServer())
      .post('/api/cfp')
      .send({
        id: 'not-a-uuid',
        name: '',
        email: 'invalid-email',
        talkTitle: '',
        isGDE: 'yes',
      })
      .expect(400);
  });

  it('should accept valid payload with 201 Created', async () => {
    const payload = {
      id: '550e8400-e29b-41d4-a716-446655440000',
      name: 'Jane Doe',
      email: 'jane@example.com',
      talkTitle: 'Signals in Angular',
      isGDE: true,
    };

    const response = await request(app.getHttpServer())
      .post('/api/cfp')
      .send(payload)
      .expect(201);

    expect(response.body).toEqual(payload);
  });
});
