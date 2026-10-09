# NOVA OS — Инструкция по сборке (BUILD.md)

## Требования для сборки ISO

Для сборки загрузочного диска NOVA OS вам понадобятся:
- Linux host (Debian / Ubuntu / Arch)
- Python 3.10+
- `xorriso`
- `squashfs-tools`
- `mtools`
- `dosfstools`
- `grub-pc-bin` и `grub-efi-amd64-bin`

## Шаг 1. Клонирование и установка зависимостей

```bash
git clone https://github.com/nova-os/nova-os.git
cd nova-os
sudo apt-get update
sudo apt-get install -y python3 xorriso squashfs-tools mtools dosfstools grub-efi-amd64-bin
```

## Шаг 2. Запуск локального тестирования

Перед сборкой ISO запустите модульные тесты компонентов:
```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```

## Шаг 3. Сборка ISO-образа

Выполните скрипт сборки ISO:
```bash
chmod +x scripts/build_iso.sh
./scripts/build_iso.sh
```

Выходной образ появится в корневом каталоге под именем `nova-os-1.0.0-x86_64.iso` вместе с `nova-os-1.0.0-x86_64.iso.sha256`.

## Шаг 4. Запуск в виртуальной машине (QEMU / KVM)

Для проверки полученного ISO в эмуляторе QEMU:
```bash
qemu-system-x86_64 -m 4G -enable-kvm -cdrom nova-os-1.0.0-x86_64.iso -boot d
```
