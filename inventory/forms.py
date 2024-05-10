from django import forms
from inventory.models import AssetCategory, Asset, Supplier, AssetUnit, Purchase, Inventory
from manager.models import Customer


class AssetCategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=32,
        label='Loại Vật tư Y-tế:',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Loại Vật-tư'})
    )

    class Meta:
        model = AssetCategory
        fields = '__all__'


class AssetUnitForm(forms.ModelForm):
    name = forms.CharField(
        max_length=32,
        label='Đơn vị tính (Y dụng cụ):',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'ĐVT Vật-tư'})
    )

    class Meta:
        model = AssetUnit
        fields = '__all__'


class AssetForm(forms.ModelForm):
    name = forms.CharField(
        max_length=80,
        label='Y dụng cụ [*]:',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Y dụng cụ'})
    )
    category = forms.ModelChoiceField(
        AssetCategory.objects.all(),
        label='Phân loại:',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    unitIN = forms.ModelChoiceField(
        AssetUnit.objects.all(),
        label='Đơn vị tính (Nhập hàng)[*]:',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    unitOUT = forms.ModelChoiceField(
        AssetUnit.objects.all(),
        label='Đơn vị tính (Xuất bán)[*]:',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    unitINOUT = forms.IntegerField(
        label='Số lượng (Xuất bán) trong 1 đơn vị tính (Nhập hàng)[*]:',
        widget=forms.NumberInput()
    )
    thumb = forms.ImageField(
        required=False,
        label='Hình ảnh:',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Asset
        fields = ('name', 'category', 'unitIN', 'unitOUT', 'unitINOUT', 'purchase', 'price', 'thumb')
        labels = {
            'purchase': 'Giá nhập:',
            'price': 'Giá bán:'
        }


class AssetFilterForm(forms.Form):
    category: forms.CharField()


class SupplierForm(forms.ModelForm):
    name = \
        forms.CharField(
            label='Nhà cung cấp:[*]',
            strip=True,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Supplier Name'})
        )
    mobile = \
        forms.CharField(
            label='Số điện thoại:[*]',
            strip=True,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Mobile Number'})
        )
    email = \
        forms.CharField(
            strip=True, required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'abc@xyz.com'})
        )
    address = \
        forms.CharField(
            label='Địa chỉ:',
            strip=True, required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Address'})
        )
    taxcode = \
        forms.CharField(
            label='Mã số thuế:[*]',
            strip=True,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MST'})
        )
    nubank = \
        forms.CharField(
            label='Số tài khoản NH:',
            strip=True, required=False,
            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Bank account'})
        )
    thumb = \
        forms.ImageField(
            required=False,
            label='Hình ảnh:',
            widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
        )

    class Meta:
        model = Supplier
        fields = '__all__'


class InventoryForm(forms.ModelForm):
    supplier = forms.ModelChoiceField(
        Supplier.objects.all(),
        label='Nhà cung cấp:',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    asset = forms.ModelChoiceField(
        Asset.objects.all(),
        label='Y dụng cụ:',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantityIO = forms.IntegerField(
        label='Số lượng:',
        widget=forms.NumberInput()
    )

    class Meta:
        model = Purchase
        fields = ('supplier',)


"""
class DeliverForm(forms.ModelForm):
    customer = forms.ModelChoiceField(
        Customer.objects.all(),
        label='Khách hàng:',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    asset = forms.ModelChoiceField(
        # Asset.objects.all(),
        Asset.objects.filter(inventory__quantityIO__gt=0).order_by('name').distinct(),
        label='Y dụng cụ:',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantityIO = forms.IntegerField(
        label='Số lượng:',
        widget=forms.NumberInput()
    )

    class Meta:
        model = Deliver
        fields = ('customer',)


class DeliverFilterForm(forms.Form):
    category: forms.CharField()
"""
