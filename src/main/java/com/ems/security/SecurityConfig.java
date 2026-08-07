package com.ems.security;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final CustomUserDetailsService userDetailsService;
    private final CustomAuthenticationSuccessHandler successHandler;
    private final CustomAuthenticationFailureHandler failureHandler;

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public DaoAuthenticationProvider authenticationProvider() {
        DaoAuthenticationProvider authProvider = new DaoAuthenticationProvider(userDetailsService);
        authProvider.setPasswordEncoder(passwordEncoder());
        return authProvider;
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration authConfig) throws Exception {
        return authConfig.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {
        http
            .csrf(csrf -> csrf
                .ignoringRequestMatchers("/h2-console/**")
            )
            .headers(headers -> headers
                .frameOptions(frame -> frame.sameOrigin())
            )
            .authorizeHttpRequests(auth -> auth
                .requestMatchers(
                    "/", "/login", "/register", "/forgot-password",
                    "/css/**", "/js/**", "/images/**", "/webjars/**", "/h2-console/**"
                ).permitAll()
                .requestMatchers("/admin/**", "/roles/**").hasRole("ADMIN")
                .requestMatchers("/employees/delete/**", "/departments/delete/**").hasRole("ADMIN")
                .requestMatchers("/employees/**", "/departments/**", "/salary/create", "/salary/edit/**").hasAnyRole("ADMIN", "HR", "MANAGER")
                .requestMatchers("/reports/**").hasAnyRole("ADMIN", "HR", "MANAGER")
                .requestMatchers("/attendance/all", "/attendance/mark").hasAnyRole("ADMIN", "HR", "MANAGER")
                .requestMatchers("/leave/approvals", "/leave/approve/**", "/leave/reject/**").hasAnyRole("ADMIN", "HR", "MANAGER")
                .requestMatchers("/dashboard", "/profile/**", "/attendance/**", "/salary/**", "/leave/**").authenticated()
                .anyRequest().authenticated()
            )
            .formLogin(form -> form
                .loginPage("/login")
                .successHandler(successHandler)
                .failureHandler(failureHandler)
                .permitAll()
            )
            .logout(logout -> logout
                .logoutUrl("/logout")
                .logoutSuccessUrl("/login?logout=true")
                .invalidateHttpSession(true)
                .deleteCookies("JSESSIONID", "remember-me")
                .permitAll()
            )
            .rememberMe(remember -> remember
                .key("emsSecretRememberMeKey2026")
                .tokenValiditySeconds(86400 * 7) // 7 days
                .userDetailsService(userDetailsService)
            );

        return http.build();
    }
}
