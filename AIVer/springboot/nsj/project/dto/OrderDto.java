package nsj.project.dto;

import java.math.BigDecimal;
import java.util.List;
import java.util.stream.Collectors;
import nsj.project.dto.CustomerDto;
import nsj.project.dto.OrderDto;
import nsj.project.dto.UserDto;
import nsj.project.entity.CustomerEntity;
import nsj.project.entity.OrderEntity;
import nsj.project.entity.UserEntity;
import nsj.project.repository.CustomerRepository;
import nsj.project.repository.OrderRepository;
import nsj.project.repository.UserRepository;
import nsj.project.service.CustomerService;
import nsj.project.service.OrderService;
import nsj.project.service.UserService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

public class OrderDto {
    private Long orId;
    private Long orCustomerId;
    private BigDecimal orAmount;

    public Long getOrId() {
        return orId;
    }

    public void setOrId(Long orId) {
        this.orId = orId;
    }

    public Long getOrCustomerId() {
        return orCustomerId;
    }

    public void setOrCustomerId(Long orCustomerId) {
        this.orCustomerId = orCustomerId;
    }

    public BigDecimal getOrAmount() {
        return orAmount;
    }

    public void setOrAmount(BigDecimal orAmount) {
        this.orAmount = orAmount;
    }
}