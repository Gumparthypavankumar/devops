package com.pocs.backend.properties;

import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import lombok.ToString;
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties("cache.redis")
@NoArgsConstructor
@Getter
@Setter
public class CacheProperties {
    private String hostName;
    private Integer hostPort;
}
