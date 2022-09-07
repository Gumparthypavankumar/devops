package com.pocs.backend.config;

import com.pocs.backend.properties.CacheProperties;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.data.redis.connection.RedisStandaloneConfiguration;
import org.springframework.data.redis.connection.jedis.JedisConnectionFactory;
import org.springframework.data.redis.core.RedisTemplate;

/*
* This collates the cache configuration using redis data store.
* This is inspired from an article. You can find the link here: https://www.baeldung.com/spring-data-redis-tutorial#the-redis-configuration
* */
@Configuration
@EnableConfigurationProperties(CacheProperties.class)
public class CacheConfig {

    private final CacheProperties cacheProperties;

    public CacheConfig(CacheProperties cacheProperties) {
        this.cacheProperties = cacheProperties;
    }

    @Bean
    public JedisConnectionFactory jedisConnectionFactory(){
        RedisStandaloneConfiguration standaloneConfiguration = new RedisStandaloneConfiguration();
        standaloneConfiguration.setPort(cacheProperties.getHostPort());
        standaloneConfiguration.setHostName(cacheProperties.getHostName());
        return new JedisConnectionFactory(standaloneConfiguration);
    }

    /*
    * Performs automatic serialization and deserialization between java objects and data in cache store
    * */
    @Bean
    public RedisTemplate<String, Object> redisTemplate() {
        RedisTemplate<String, Object> template = new RedisTemplate<>();
        template.setConnectionFactory(jedisConnectionFactory());
        return template;
    }
}
